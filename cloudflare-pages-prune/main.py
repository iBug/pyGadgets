#!/usr/bin/python3

import datetime
import json
import os
import requests
import sys


class Cloudflare:
    def __init__(self, account_id: str, api_token: str):
        self.account_id = account_id
        self.api_token = api_token
        self.s = requests.Session()
        self.s.headers.update({
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.api_token}",
        })

    @property
    def base_url(self) -> str:
        return f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/pages/projects"

    def projects(self):
        res = self.s.get(self.base_url)
        res.raise_for_status()
        return res.json()["result"]

    def deployments(self, project_name: str):
        url = f"{self.base_url}/{project_name}/deployments"
        res = self.s.get(url)
        res.raise_for_status()
        return res.json()["result"]

    def delete_deployment(self, project_name: str, deployment_id: str):
        url = f"{self.base_url}/{project_name}/deployments/{deployment_id}"
        res = self.s.delete(url)
        return res.json()


def main():
    os.chdir(os.path.dirname(__file__))
    with open("config.json", "r") as f:
        config = json.load(f)
    cf = Cloudflare(config["account-id"], config["api-token"])

    now = datetime.datetime.now()
    expiry = datetime.timedelta(days=30)

    for proj in cf.projects():
        project_name = proj["name"]
        print(f"Working on {project_name}", end="")
        deployments = cf.deployments(project_name)
        print(f", {len(deployments)} deployments")
        for depl in deployments:
            if depl["id"] == proj["canonical_deployment"]["id"]:
                continue
            if depl["aliases"]:
                # has an active deployment, skip
                continue

            if depl["is_skipped"]:
                print(f"  Delete {depl['short_id']}: is skipped")
                cf.delete_deployment(project_name, depl["id"])
                continue

            created_on = datetime.datetime.fromisoformat(depl["created_on"].split(".")[0])
            delta = now - created_on
            if delta >= expiry:
                print(f"  Delete {depl['short_id']}: is {delta.days} days old")
                cf.delete_deployment(project_name, depl["id"])
                continue


if __name__ == "__main__":
    main()
