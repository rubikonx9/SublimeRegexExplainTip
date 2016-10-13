# SublimeRegexExplainTip
SublimeText 3 plugin for displaying regular expression explanations

## What it looks like

![Screenshot](/screenshots/1.PNG)

## Why?

As some regular expressions are *write-only* code, it's sometimes useful to obtain a description of what a particular regex actually does.
Having it available in a text editor can be an asset.

## Installation

Install via [Package Control](https://packagecontrol.io/).
Alternatively, clone this repository to `Packages` directory.

## How to use

Press <kbd>Alt</kbd>+<kbd>R</kbd> to display the explanation of selected text.
Currently, a region must be explicitly selected.

## Dependencies

The plugin uses [YAPE::Regex::Explain](http://search.cpan.org/dist/YAPE-Regex-Explain/Explain.pm) to obtain the regex explanation.
Therefore, Perl with `YAPE::Regex::Explain` module installed is required.
