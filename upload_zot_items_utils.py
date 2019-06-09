#!/usr/bin/python3.6

import re

from datetime import datetime


formatted_strings = {
    # Components
    "Access Control": "comp_access_control",
    "Analytics": "comp_analytics",
    "Atlas": "comp_atlas",
    "Auditing": "comp_auditing",
    "Automation Infrastructure": "comp_automation_infrastructure",
    "Build": "comp_build",
    "EV": "comp_ev",
    "HL7": "comp_hl7",
    "IAE/PRAE": "comp_iae_prae",
    "Image Corrections/Deletions": "comp_image_corrections_deletions",
    "Image Workflow": "comp_image_workflow",
    "InteleBrowser": "comp_intelebrowser",
    "InteleConnect": "comp_inteleconnect",
    "InteleViewer": "comp_inteleviewer",
    "Monitoring": "comp_monitoring",
    "Peer Review": "comp_peer_review",
    "PEP": "comp_pep",
    "Replication": "comp_replication",
    "Report Distribution": "comp_report_distribution",
    "Reporting Workflow": "comp_reporting_workflow",
    "Technical Services": "comp_technical_services",
    "User Service": "comp_user_service",
    # Types
    "Bug": "type_bug",
    "Enhancement": "type_enhancement",
    "Epic": "type_epic",
    "Release Project": "type_release_project",
    "Task": "type_task",
    "Technical Debt": "type_technical_debt"
    #
}


def transform(key):
    """Return the formatted equivalent of a given string."""
    value = formatted_strings[key]
    if value:
        return value
    else:
        return key


def sort_pacs_versions(pacs_versions):
    """Return meaningfully sorted list of PACS versions."""
    early_versions = []
    late_versions = []
    for version in pacs_versions:
        if len(version) == 10:
            early_versions.append(version)
        else:
            late_versions.append(version)
    early_versions.sort()
    late_versions.sort()
    return early_versions + late_versions


def format_jira_date(jira_date):
    """Return simple date format of Jira date
       Sample Jira Date    : Wed, 22 May 2019 13:40:38 -0400
       Sample Simple Format: 2019_0522
    """
    regex = re.compile(r'[\w]+, ([\d]+) ([\w]+) ([\d]+) .*')

    search_obj = regex.search(jira_date)
    day = search_obj.group(1)
    month = search_obj.group(2)
    year = search_obj.group(3)

    datetime_obj = datetime.strptime('%s %s %s' % (day.zfill(2), month, year), '%d %b %Y')
    return datetime_obj.strftime('%Y_%m%d')
