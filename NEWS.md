# 0.2.0

Added the `--modes` flag.

4 modes are available:

## simple

Simply replace every formatting sequence with a space.

```
| before <color:blue>Blue Text</color> after |
| before             Blue Text         after |
```

## align_left

The replacement whitespace with will be added to the right of
**all following** text.

```
| before <color:blue>Blue Text</color> after |
| before Blue Text after                     |
```

## center_ws

Centers the text **within** the replacement whitespace.
In case of uneven whitespace, the right side will contain one
more space than the left side.

```
| before <color:blue>Blue Text</color> after |
| before           Blue Text           after |
```

## center_line

Centers the line within the bounds.

```
| before <color:blue>Blue Text</color> after |
|           before Blue Text after           |
```

# 0.1.0

* Initial Release
