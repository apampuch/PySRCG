Are you a fan of Shadowrun 3rd edition? Do you want a character generator for it that actually works, unlike NSRCG?

Look no further than PySRCG!
* Written in Python, for maximum compatibility across operating systems.
* Serializes all data in .json format, for maximum readability and editability.

Notes on the .json file generated for character saves:

The `base_attributes` refers to the attribute value before ALL modifiers. 
For example, an ork with Body 4 with no cyberware, etc. would show up as `"body": 1` in the .json save, since they have
a +3 racial modifier to body.
Furthermore, an intelligence of 1 would show up as `"intelligence": 2` since they have a -1 modifier to intelligence.
Be careful when manually editing these values especially!

Possible dependency: sudo apt-get install idle3
