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
 - Find out if this is valid:
```
move r1 5
alias BOB rr1
move BOB 50
move r1 6
move BOB 100
```

 - Find out if this will error:
```
and r1 2.2 3
```

TODO:
 - Stack functions relating to other devices <-- Needs to be tested in game
 - Load functions relating to other devices
 - Set functions relating to other devices
 - Branch instructions relating to other devices <-- WORK ON
 - Aliases for devices
 - Select Command
 - Add bit shifting
 - Slot loading
 - Check all slot types in game
 - Reading slot values
 - Network Channels
 - Full slot support