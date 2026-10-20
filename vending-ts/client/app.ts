// This script runs in the browser. It asks the server for data and changes
// the page to match what the server says.

// The shape of one slot, as the server sends it. This type is a promise about
// the JSON, and nothing checks it while the program runs.
type Slot = {
  slot_id: string;
  item_name: string;
  price_cents: number;
  stock: number;
};

// The shape of an error message from the server.
type ApiError = { error: string };

// Find an element by its id, or stop with a clear message if it is missing.
// getElementById returns "an element or null", and TypeScript makes us deal
// with the null before we use the result.
function findElementById(id: string): HTMLElement {
  const element = document.getElementById(id);
  if (element === null) {
    throw new Error(`The page has no element with id "${id}".`);
  }
  return element;
}

// Find the elements that we need, once, when the script loads.
const slotListElement = findElementById("slots");
const statusElement = findElementById("status");
// "as HTMLTemplateElement" tells the compiler something that we know about our own page.
const slotTemplate = findElementById("slot-template") as HTMLTemplateElement;

// A formatter from the browser that writes prices in euros, so that 1.75
// becomes €1.75.
const euroFormatter = new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR" });

// Send a request to our API and return the JSON from the reply. The function
// is async, so it can wait for the network without freezing the page.
// <T> is the type that the caller expects the JSON to have.
async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    // fetch sends the request and returns a promise of a response.
    // "await" pauses this function until the response arrives.
    response = await fetch(url, options);
  } catch {
    // fetch fails like this only when no reply arrives at all, for example
    // when the server is not running.
    throw new Error("Cannot reach the server. Is it running?");
  }

  // The body of the reply is JSON text. json() parses it into an object.
  // The compiler cannot know what the server sent, so the type is "unknown".
  const data: unknown = await response.json();

  // A reply can arrive with a bad status such as 404 or 409.
  // response.ok is false for those, so we pass the server's message on.
  if (!response.ok) {
    throw new Error((data as ApiError).error);
  }
  return data as T;
}

// Build one card for one slot. The card is not on the page until we add it.
function createSlotCard(slot: Slot): HTMLElement {
  // Copy the card layout from the template in index.html. The ! says "this is
  // never null", because we wrote the template ourselves.
  const slotCard = slotTemplate.content.firstElementChild!.cloneNode(true) as HTMLElement;
  const isSoldOut = slot.stock === 0;

  // data-slot remembers which slot this card belongs to, for the click handler.
  slotCard.dataset.slot = slot.slot_id;

  // The sold-out class lets the stylesheet decide how a sold-out card looks.
  slotCard.classList.toggle("sold-out", isSoldOut);

  // textContent treats a value as plain text, never as HTML, so data from the
  // server can never run as code in the page.
  slotCard.querySelector(".item-name")!.textContent = `${slot.slot_id}: ${slot.item_name}`;

  // Prices are stored in cents. We divide by 100 only when we show them.
  slotCard.querySelector(".price")!.textContent = euroFormatter.format(slot.price_cents / 100);

  slotCard.querySelector(".stock")!.textContent = isSoldOut ? "Sold out" : `${slot.stock} left`;
  slotCard.querySelector("button")!.disabled = isSoldOut;
  return slotCard;
}

// Ask the server for every slot and show them all on the page.
async function loadAllSlots(): Promise<void> {
  try {
    const slots = await requestJson<Slot[]>("/api/slots");

    // map turns a list of slot data into a list of cards.
    // replaceChildren puts the cards on the page. This changes the DOM, and
    // the browser then redraws the screen.
    slotListElement.replaceChildren(...slots.map(createSlotCard));
    statusElement.textContent = "Choose a snack.";
  } catch (error) {
    // Inside catch, TypeScript treats "error" as unknown, so we say what it is.
    statusElement.textContent = (error as Error).message;
  }
}

// One listener on the whole list handles clicks on every Buy button. This
// technique is called event delegation, and it also covers buttons that the
// script adds later.
slotListElement.addEventListener("click", async (event) => {
  // closest() climbs from the clicked element up to the nearest Buy button.
  // It returns null when the click landed somewhere else.
  const buyButton = (event.target as HTMLElement).closest("button.buy");
  if (buyButton === null) {
    return;
  }

  const slotCard = buyButton.closest("article")!;
  try {
    // POST asks the server to change something. The reply is the updated slot.
    const updatedSlot = await requestJson<Slot>(`/api/slots/${slotCard.dataset.slot}/buy`, {
      method: "POST",
    });

    // Replace only this card, using what the server says and not what we guess.
    slotCard.replaceWith(createSlotCard(updatedSlot));
    statusElement.textContent = `Enjoy your ${updatedSlot.item_name}!`;
  } catch (error) {
    statusElement.textContent = (error as Error).message;
  }
});

// Show the slots as soon as the page opens.
loadAllSlots();
