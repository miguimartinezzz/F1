YEAR = 2023
RACE = 'Bahrain'
SESSION = 'Q'

# ELIGE LA SESION QUE QUIERAS

session = ff1.get_session(
    YEAR,
    RACE,
    SESSION
)
# CARGA LA SESIÓN

session.load()

# ANALIZAMOS LOS DATOS Y ELEGIMOS LOS QUE QUEREMOS

laps = session.laps
laps.pick_fastest()
ALO = laps.pick_driver('ALO')
ALO_LAPS = ALO.pick_fastest()

ALO_LAPS.get_car_data()