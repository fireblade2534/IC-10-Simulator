 - Check if refrencing NaN in an indrect reference produces an error:
```
div r2 0 0

move rr2 10
```

 - Check if overwriting a constant or a alias works:
```
define Bob 10

alias Bob r1

define Bob 3
```

 - Check if this errors or if it just continues on:
```
div r2 0 0

jr -5
move r1 35
```

 - Find out what happens when you put NaN into all combos of arguments in the branch instructions
 
 - Find out if it errors when you do a float in an inderect reference:
```
move r1 2
move r2 3.2
move rrr1 69.3
```