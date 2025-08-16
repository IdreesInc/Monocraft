# Contributing to Monocraft

Contributions to the font are always welcome, though please be sure to adhere to these guidelines if you want your changes to be approved.

If you have any questions or want to run something by a contributor, contact us on the [Discord](https://discord.gg/6yxE9prcNc)

## Guiding Principles of Monocraft

- Characters must look exactly the same as they do in Minecraft unless there's a good reason not to do so
  - The only exception is if the character is too wide to fit in the font and still be monospaced. In this case, we would modify the glyph to fit if possible. Such modifications will likely need to be run by [@IdreesInc](https://github.com/IdreesInc) first to ensure that the style is kept consistent with other glyphs
  - Note that characters like "i" and "t" have been modified with tails to appear slightly wider, this is also allowed on a case by case basis
- Ligatures must always be helpful and never annoying
  - This means that ligatures that might work in one context (like <= as an arrow) but fail in another (like when <= should instead be "less than or equal to") should not be added to Monocraft
  - As a rule, it's usually better to only add ligatures that someone might expect rather than every possible ligature so as to avoid ligatures appearing out of place
- The code that generates Monocraft should be clean, consistent, and maintainable
  - If you feel as if a feature would be hard to add cleanly, contact [@IdreesInc](https://github.com/IdreesInc) instead and I'll see if we can work something out

So long as you keep in line with the above principles, your PR is much more likely to be merged. Good luck!
