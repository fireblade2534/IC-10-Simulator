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