# SublimeRegexExplainTip
SublimeText 3 plugin for displaying regular expression explanations

## What it looks like

![Screenshot](https://raw.githubusercontent.com/rubikonx9/SublimeRegexExplainTip/master/screenshots/1.PNG)

## Why?

As some regular expressions are *write-only* code, it's sometimes useful to obtain a description of what a particular regex actually does.
Having it available in a text editor can be an asset.

## Installation

Install via [Package Control](https://packagecontrol.io/).
Alternatively, clone this repository to `Packages` directory.

## How to use

Press <kbd>Shift</kbd>+<kbd>Super</kbd>+<kbd>Alt</kbd>+<kbd>R</kbd> to display the explanation of selected text.
Currently, a region must be explicitly selected.

## Customization

It is possible to use custom CSS files. You can define the CSS file in settings file (navigate to `Preferences` -> `Package Settings` -> `RegexExplainTip` -> `Settings - User`) under `css_file` key:

```
{
    "css_file": "Packages/User/my-custom.css"
}
```

You should locate the file somewhere under `Packages` (`Preferences` -> `Browse Packages...`) directory.

## Dependencies

The plugin uses [YAPE::Regex::Explain](http://search.cpan.org/dist/YAPE-Regex-Explain/Explain.pm) to obtain the regex explanation.
Therefore, Perl with `YAPE::Regex::Explain` module installed is required.

## Caveats

As this plugin relies on external Perl installation and modules, one must have correct environment setup.
This includes proper value if Perl's `@INC` variable, which allows Perl to find required modules.
This directory depends on you environment settings, OS, CPAN configuration and so on.

For example, you might need to define the paths in `PERL5LIB` variable:

`export PERL5LIB=/some/perl/installation/directory/lib`.

Alternatively, one may add the following line to Perl code declared in `get_explanation` method:

`use lib 'c:/StrawberryPERL/perl/site/lib';`
