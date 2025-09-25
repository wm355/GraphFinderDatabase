# VO2 Dopants Database

A web application for exploring and visualizing VO2 (Vanadium Dioxide) dopant data, including resistance and transmittance measurements across different temperatures and concentrations.

## Software Stack

- **Flask** - Backend framework
- **Vue.js** - Frontend framework
- **CSV Data** - File-based data storage organized in nested folders

## Database Structure

The data is organized in a hierarchical folder structure under `flask-backend/input/`:

```
flask-backend/
└── input/
    ├── resistance_temp/           # Resistance vs Temperature data
    │   ├── B/                     # Boron dopant
    │   │   ├── b_0_cooling.csv
    │   │   ├── b_0_heating.csv
    │   │   ├── b_0.5_cooling.csv
    │   │   ├── b_0.5_heating.csv
    │   │   └── b_1.3_cooling.csv
    │   │   └── b_1.3_heating.csv
    │   ├── Cr/                    # Chromium dopant
    │   │   ├── cr_0_cooling.csv
    │   │   ├── cr_0_heating.csv
    │   │   ├── cr_1_cooling.csv
    │   │   ├── cr_1_heating.csv
    │   │   ├── cr_3_cooling.csv
    │   │   ├── cr_3_heating.csv
    │   │   ├── cr_4_cooling.csv
    │   │   ├── cr_4_heating.csv
    │   │   ├── cr_10_cooling.csv
    │   │   ├── cr_10_heating.csv
    │   │   ├── cr_14_cooling.csv
    │   │   └── cr_14_heating.csv
    │   ├── Fe/                    # Iron dopant
    │   │   ├── fe_0_cooling.csv
    │   │   ├── fe_0_heating.csv
    │   │   ├── fe_0.6_cooling.csv
    │   │   ├── fe_0.6_heating.csv
    │   │   ├── fe_1.2_cooling.csv
    │   │   ├── fe_1.2_heating.csv
    │   │   ├── fe_2.0_cooling.csv
    │   │   ├── fe_2.0_heating.csv
    │   │   ├── fe_3.0_cooling.csv
    │   │   ├── fe_3.0_heating.csv
    │   │   ├── fe_4.0_cooling.csv
    │   │   ├── fe_4.0_heating.csv
    │   │   ├── fe_5.0_cooling.csv
    │   │   └── fe_5.0_heating.csv
    │   ├── Mo/                    # Molybdenum dopant
    │   │   ├── mo_0_cooling.csv
    │   │   ├── mo_0_heating.csv
    │   │   ├── mo_1_cooling.csv
    │   │   ├── mo_1_heating.csv
    │   │   ├── mo_3_cooling.csv
    │   │   ├── mo_3_heating.csv
    │   │   ├── mo_5_cooling.csv
    │   │   └── mo_5_heating.csv
    │   └── Nb/                    # Niobium dopant
    │       ├── nb_0_cooling.csv
    │       ├── nb_0_heating.csv
    │       ├── nb_5_cooling.csv
    │       ├── nb_5_heating.csv
    │       ├── nb_10_cooling.csv
    │       ├── nb_10_heating.csv
    │       ├── nb_15_cooling.csv
    │       ├── nb_15_heating.csv
    │       ├── nb_20_cooling.csv
    │       └── nb_20_heating.csv
    └── transmittance_temp/        # Transmittance vs Temperature data
        ├── Ta/                    # Tantalum dopant
        │   ├── ta_2_cooling_transmittance.csv
        │   ├── ta_2_heating_transmittance.csv
        │   ├── ta_3.5_cooling_transmittance.csv
        │   ├── ta_3.5_heating_transmittance.csv
        │   ├── ta_4_cooling_transmittance.csv
        │   ├── ta_4_heating_transmittance.csv
        │   ├── ta_5_cooling_transmittance.csv
        │   ├── ta_5_heating_transmittance.csv
        │   ├── ta_6.5_cooling_transmittance.csv
        │   └── ta_6.5_heating_transmittance.csv
        └── W/                     # Tungsten dopant
            ├── w_0_cooling_transmittance.csv
            ├── w_0_heating_transmittance.csv
            ├── w_0.5_cooling_transmittance.csv
            ├── w_0.5_heating_transmittance.csv
            ├── w_0.5_mol_cooling_transmittance.csv
            ├── w_0.5_mol_heating_transmittance.csv
            ├── w_1.0_cooling_transmittance.csv
            ├── w_1.0_heating_transmittance.csv
            ├── w_1.0_mol_cooling_transmittance.csv
            ├── w_1.0_mol_heating_transmittance.csv
            ├── w_1.5_mol_cooling_transmittance.csv
            ├── w_1.5_mol_heating_transmittance.csv
            ├── w_2.0_cooling_transmittance.csv
            ├── w_2.0_heating_transmittance.csv
            ├── w_2.0_mol_cooling_transmittance.csv
            └── w_2.0_mol_heating_transmittance.csv
```

## Dopant Types

- **B** (Boron) - Concentrations: 0%, 0.5%, 1.3%
- **Cr** (Chromium) - Concentrations: 0%, 1%, 3%, 4%, 10%, 14%
- **Fe** (Iron) - Concentrations: 0%, 0.6%, 1.2%, 2.0%, 3.0%, 4.0%, 5.0%
- **Mo** (Molybdenum) - Concentrations: 0%, 1%, 3%, 5%
- **Nb** (Niobium) - Concentrations: 0%, 5%, 10%, 15%, 20%
- **Ta** (Tantalum) - Concentrations: 2%, 3.5%, 4%, 5%, 6.5%
- **W** (Tungsten) - Concentrations: 0%, 0.5%, 1.0%, 2.0% (including mol% variants)


