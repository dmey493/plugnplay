import { removeBackground } from "@imgly/background-removal-node";
import { readFileSync, writeFileSync } from "fs";
import { resolve } from "path";

const inputPath = resolve("public/hero-photo.png");
const outputPath = resolve("public/hero-cutout.png");

console.log("Reading image...");
const inputBuffer = readFileSync(inputPath);
const blob = new Blob([inputBuffer], { type: "image/png" });

console.log("Removing background (this may take a minute on first run)...");
const resultBlob = await removeBackground(blob);

console.log("Saving result...");
const arrayBuffer = await resultBlob.arrayBuffer();
writeFileSync(outputPath, Buffer.from(arrayBuffer));

console.log(`Done! Saved to ${outputPath}`);
