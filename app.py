from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests

app = Flask("JobScrapper")

cache = {}


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/search")
def search():
    keyword = request.args.get("keyword")
    if keyword in cache:
        results = cache[keyword]
    else:
        results = scrape_from_remoteok(keyword) + scrape_from_weworkremotely(keyword)
        cache[keyword] = results
    return render_template("search.html", keyword=keyword, results=results)


def scrape_from_remoteok(keyword):
    url = f"https://remoteok.com/remote-{keyword}-jobs"
    request = requests.get(url, headers={"User-Agent": "Kimchi"})
    results = []

    if request.status_code == 200:
        soup = BeautifulSoup(request.text, "html.parser")
        jobs = soup.find_all("tr", class_="job")

        for job in jobs:
            company = job.find("h3", itemprop="name")
            position = job.find("h2", itemprop="title")
            location = job.find("div", class_="location")
            link = job.find("a", class_="preventLink")
            image = link.find("img", class_="logo")

            if company:
                company = company.string.strip()
            if position:
                position = position.string.strip()
            if location:
                location = location.string.strip()
            if link:
                link = link["href"]
            if image:
                image = image["data-src"]

            if company and position and location and image and link:
                job = {
                    "origin": "remoteok.com",
                    "company": company,
                    "position": position,
                    "location": location,
                    "link": f"https://remoteok.com{link}",
                    "image": image,
                }
                results.append(job)

    else:
        print("Can't get jobs.")

    return results


def scrape_from_weworkremotely(keyword):
    url = f"https://weworkremotely.com/remote-jobs/search?term={keyword}"
    request = requests.get(url, headers={"User-Agent": "Kimchi"})
    results = []
    if request.status_code == 200:
        soup = BeautifulSoup(request.text, "html.parser")
        sections = soup.find_all("section", class_="jobs")
        jobs = []
        for section in sections:
            jobs += section.find_all("li")

        for job in jobs:
            company = job.find("span", class_="company")
            position = job.find("span", class_="title")
            location = job.find("span", class_="region")
            link = job.find_all("a")[-1]
            image = job.find("div", class_="flag-logo")

            if company:
                company = company.string.strip()
            if position:
                position = position.string.strip()
            if location:
                location = location.string.strip()
            if link:
                link = link["href"]
            if image:
                image = image["style"]

            if company and position and location and image and link:
                job = {
                    "origin": "weworkremotely.com",
                    "company": company,
                    "position": position,
                    "location": location,
                    "link": f"https://weworkremotely.com/{link}",
                    "image": image[21:],
                }
                results.append(job)
    else:
        print("Can't get jobs.")
    return results


if __name__ == "__main__":
    app.run(debug=True)
