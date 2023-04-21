import sqlite3
import matplotlib.pyplot as plt

def query_function(statement: str):
    conn = sqlite3.connect("harry_potter.db")
    c = conn.cursor()
    result = c.execute(statement).fetchall()
    c.close()
    return result

def calculate_proportion():
    result = query_function("SELECT house, COUNT(*) FROM characters WHERE house <> '' GROUP BY house")
    house_count = dict(result)
    result = query_function("SELECT house, COUNT(*) FROM characters WHERE alive = 0 AND house <> '' GROUP BY house")
    deceased_count = dict(result)
    proportion_sum = sum(deceased_count.get(house, 0) / house_count.get(house, 1) for house in house_count)
    proportion = {house: deceased_count.get(house, 0) / house_count.get(house, 1) / proportion_sum for house in house_count}
    return proportion

def calculate_wand_material():
    result = query_function(
        "SELECT core, COUNT(*) FROM characters JOIN wands ON characters.character_id = wands.character_id WHERE house = 'Gryffindor' AND core != '' GROUP BY core ORDER BY COUNT(*) DESC")

    # Convert the query result to a dictionary
    dict_result = dict(result)
    return {'Gryffindor': dict_result}


def write_data_to_file(data, filename):
    with open(filename, "w") as f:
        f.write("Proportion of Deceased Characters in Each Hogwarts House:\n")
        for house, proportion in data.items():
            f.write(f"{house}: {proportion}\n")
        f.write("\nMost Common Wand Cores in Gryffindor:\n")
        for house, cores in calculate_wand_material().items():
            for core, frequency in cores.items():
                f.write(f"{house}: {core}: {frequency}\n")
        

def plot_deceased_by_house(deceased_by_house):
    houses = list(deceased_by_house.keys())
    counts = list(deceased_by_house.values())
    colors = ['#cd373c', '#E9AC2D', '#082664', '#2A623D']
    plt.rcParams["figure.figsize"] = (20,4)
    plt.pie(counts, labels=houses, labeldistance=1.15, colors=colors, autopct='%1.1f%%')
    plt.title("Proportion of Deceased Characters in Each Hogwarts House")
    plt.show()

def plot_wand_cores(wand_cores):
    cores = list(wand_cores['Gryffindor'].keys())
    counts = list(wand_cores['Gryffindor'].values())
    colors = ['#AC94F4', '#F7BE6D', '#F94449']
    plt.rcParams["figure.figsize"] = (10,4)
    plt.bar(cores, counts, color=colors)
    plt.title('Most Common Wand Cores in Gryffindor')
    plt.xlabel('Wand Cores')
    plt.ylabel('Frequency')
    plt.show()

def main():
    data = calculate_proportion()
    write_data_to_file(data, "calculations.txt")
    plot_deceased_by_house(data)
    wand_data = calculate_wand_material()
    plot_wand_cores(wand_data)


if __name__ == "__main__":
    main()