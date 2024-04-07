def get_skor(data: dict, portion: list):
    # Perhitungan dan pengelompokkan faktor
    for key_sub, val_sub in data.items():
        for key_factor, val_factor in val_sub.items():
            data[key_sub][key_factor] = sum(data[key_sub][key_factor]) / len(data[key_sub][key_factor])

    # Perhitungan nilai berdasarkan variabel
    for key_sub, val_sub in data.items():
        data[key_sub] = 0.7 * val_sub["CORE"] + 0.3 * val_sub["SECONDARY"]

    # Perhitungan nilai final
    res = []
    items = list(data.items())
    for i in range(len(portion)):
        res.append(items[i][1] * (portion[i] / 100))

    # Mengembalikan nilai akhir
    return sum(res)
