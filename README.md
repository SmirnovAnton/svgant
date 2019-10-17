# svgant (WIP)

## requires: 
    
- takes 'datalist.csv' as input, like this:

`START\tEND\tLABEL`

`2019-01-01 15:22\t2019-01-02\tsome comment to appear on svg (not too much)`

- Pandas v0.25

## how to use

 1. put this and the input file in folder, check Pandas (and the other packages)
 2. then just run the cell below -> output will be 'svgOut.svg'
 3. params can be changed below in svgParameters

## Next dev steps: 

 1. get feedback 
 2. nice argparse
 3. implement feedback 
 4. thorough testing (maybe need one more overlap check in loop?)
 5. comment nicely and make standalone script, maybe pip package
 6. go over TODOS
 7. redo as PWM app? 

## various TODOS:

 - import ical and the like
 - multiline solutions and options
 - overlaps ? duplicates ? 
 - color palette, shading, whatever
 - event line breaking? prob. yes?
 - pandas min 25, others too
 - colorblind palettes
 - check within loop something

## notes

- this is essentially a Gantt diagram creator, of which there are tons around, but they do seem clunky
