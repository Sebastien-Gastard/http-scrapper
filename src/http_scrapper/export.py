import csv


def save_to_csv_http(filename, data):
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Source page", "HTTP link found"])
        writer.writerows(data)


def save_to_csv_404(filename, data):
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Source page", "404 link"])
        writer.writerows(data)
