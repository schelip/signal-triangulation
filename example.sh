touch ./receptors_data_example.json
echo '[
    {
        "x": 1.55,
        "y": 17.63,
        "p0": -26.0,
        "L": 2.1
    },
    {
        "x": -4.02,
        "y": 0.0,
        "p0": -33.8,
        "L": 1.8
    },
    {
        "x": -4.4,
        "y": 9.6,
        "p0": -29.8,
        "L": 1.3
    },
    {
        "x": 9.27,
        "y": 4.64,
        "p0": -31.2,
        "L": 1.4
    },
    {
        "x": 9.15,
        "y": 12,
        "p0": -33.0,
        "L": 1.5
    }
]' > receptors_data_example.json

printf 'Exemplo 1 (0.00, 9.00)\n'
py signal_triangulation.py receptors_data_example.json -v -48.4 -50.6 -32.2 -47.4 -46.3 -p 4 \

printf '\nExemplo 2 (3.00, 3.00)\n'
py signal_triangulation.py receptors_data_example.json -v -46.9 -46.4 -41.2 -45.8 -48.7 -p 2 \

