# signal-triangulation
Program that receives potency values for a signal and triangulates the position of the emissor based on the positions and attenuation coeficients of the receptors

The data of the receptors must be defined in a json file which will be passed as the first argument
```json
[
    {
        "x": 1.55, // x position of the receptor
        "y": 17.63, // y position of the receptor
        "p0": -26.0, // base potency value, measured at 1 meter distance
        "L": 2.1 // estimated potency attenuation factor
    },
    ...
]
```

Then, the program can be start on interactive mode (which will ask for the potency values of each receptor, one by one), or the potency values can be passed as the next n arguments.

```
$ py signal_triangulation.py [<path_to_receiver_data>] [-i|-v] [<values>...]
```

Running `./example.sh` will generate a sample receptor data json and run the triangulation for two example emissors

```
$ ./example.sh

Exemplo 1 (3.00, 3.00)
Receptor position coeficients matrix: 
[[-11.9  -16.06]
 [ -0.76  19.2 ]
 [-27.34   9.92]
 [-27.1   -4.8 ]]

System results matrix:
[-68.10384126 166.5837451  207.9160206  -59.20452172]

Estimated position: (-2.28688615984768, 8.983563450819503)

Exemplo 2 (0.00, 9.00)
Receptor position coeficients matrix: 
[[-11.9  -16.06]
 [ -0.76  19.2 ]
 [-27.34   9.92]
 [-27.1   -4.8 ]]

System results matrix:
[-160.60282728   63.74410513   69.14193202  -48.96208288]

Estimated position: (0.6630668037231463, 6.284152330037825)
```
