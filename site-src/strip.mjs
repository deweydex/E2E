// Remove TypeScript types from a file and print the JavaScript that remains.
import { stripTypeScriptTypes } from "node:module";
import { readFileSync } from "node:fs";

process.stdout.write(stripTypeScriptTypes(readFileSync(process.argv[2], "utf8"), { mode: "strip" }));
