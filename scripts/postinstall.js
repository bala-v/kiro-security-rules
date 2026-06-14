#!/usr/bin/env node
/**
 * npm postinstall script for kiro-security-rules.
 * Copies steering files, hooks, and templates to the project's .kiro/ directory.
 */
const fs = require("fs");
const path = require("path");

const PKG_DIR = path.resolve(__dirname, "..");
const TARGET_DIR = process.env.INIT_CWD || process.cwd();
const KIRO_DIR = path.join(TARGET_DIR, ".kiro");

function copyIfNotExists(src, dest, filename) {
  const destPath = path.join(dest, filename);
  if (fs.existsSync(destPath)) {
    console.log(`  SKIP ${filename} (already exists)`);
    return false;
  }
  fs.copyFileSync(src, destPath);
  console.log(`  COPY ${filename}`);
  return true;
}

function copyDirRecursive(srcDir, destDir) {
  if (!fs.existsSync(srcDir)) return 0;
  fs.mkdirSync(destDir, { recursive: true });
  let count = 0;
  for (const entry of fs.readdirSync(srcDir)) {
    const srcPath = path.join(srcDir, entry);
    const destPath = path.join(destDir, entry);
    if (fs.statSync(srcPath).isDirectory()) {
      count += copyDirRecursive(srcPath, destPath);
    } else if (entry.endsWith(".md") || entry.endsWith(".json")) {
      copyIfNotExists(srcPath, destDir, entry);
      count++;
    }
  }
  return count;
}

console.log("Installing Kiro Security Rules...");

fs.mkdirSync(path.join(KIRO_DIR, "steering"), { recursive: true });
fs.mkdirSync(path.join(KIRO_DIR, "hooks"), { recursive: true });

let count = 0;

// Copy all steering files
const srcSteering = path.join(PKG_DIR, "steering");
for (const subdir of ["always", "conditional", "manual"]) {
  const src = path.join(srcSteering, subdir);
  if (fs.existsSync(src)) {
    fs.mkdirSync(path.join(KIRO_DIR, "steering"), { recursive: true });
    count += copyDirRecursive(src, path.join(KIRO_DIR, "steering"));
  }
}

// Copy hooks
const srcHooks = path.join(PKG_DIR, "hooks");
count += copyDirRecursive(srcHooks, path.join(KIRO_DIR, "hooks"));

console.log(`\nDone. ${count} files installed to ${KIRO_DIR}`);
console.log("Run 'kiro-security-check validate' to verify installation.");
