#!/usr/bin/python3.6

import re

from datetime import datetime


formatted_strings = {
    # Components
    "Access Control": "component_access_control",
    "Analytics": "component_analytics",
    "Atlas": "component_atlas",
    "Auditing": "component_auditing",
    "Automation Infrastructure": "component_automation_infrastructure",
    "Build": "component_build",
    "EV": "component_ev",
    "HL7": "component_hl7",
    "IAE/PRAE": "component_iae_prae",
    "Image Corrections/Deletions": "component_image_corrections_deletions",
    "Image Workflow": "component_image_workflow",
    "InteleBrowser": "component_intelebrowser",
    "InteleConnect": "component_inteleconnect",
    "InteleViewer": "component_inteleviewer",
    "Monitoring": "component_monitoring",
    "Peer Review": "component_peer_review",
    "PEP": "component_pep",
    "Replication": "component_replication",
    "Report Distribution": "component_report_distribution",
    "Reporting Workflow": "component_reporting_workflow",
    "Technical Services": "component_technical_services",
    "User Service": "component_user_service",
    # Types
    "Bug": "type_bug",
    "Enhancement": "type_enhancement",
    "Epic": "type_epic",
    "Problem": "type_problem",
    "Release Project": "type_release_project",
    "Story": "type_story",
    "Sub-task": "type_sub_task",
    "Task": "type_task",
    "Technical Debt": "type_technical_debt"
}


def transform(key):
    """Return the formatted equivalent of a given string."""
    return formatted_strings[key]


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
