# Cybersecurity-Projects
# Basic Pentesting 1 — VulnHub CTF Walkthrough

A penetration testing exercise completed as part of the HyperionDev Cyber Security 
Bootcamp, targeting the "Basic Pentesting 1" VulnHub machine.

## Overview
This project demonstrates a full penetration test against a deliberately vulnerable 
Linux VM, covering reconnaissance, exploitation, and post-exploitation phases using 
industry-standard tools.

## Environment
- **Attacker machine:** Kali Linux
- **Target:** Basic Pentesting 1 (VulnHub)
- **Virtualization:** VirtualBox
- **Tools used:** Nmap, Metasploit Framework, ...

## Methodology

### 1. Reconnaissance
- Nmap scan to identify open ports and running services
- Identified ProFTPD 1.3.3c running on port 21

### 2. Exploitation
- Identified a known backdoor vulnerability in ProFTPD 1.3.3c
- Used Metasploit to gain a shell on the target

### 3. Post-Exploitation
- Extracted password hashes from the target
- [Add any privilege escalation steps you did]

## Key Findings
Outdated service versions (e.g. ProFTPD 1.3.3c) can contain known backdoors that 
allow trivial remote code execution. This highlights the importance of keeping 
software patched.

## Skills Demonstrated
- Network reconnaissance & port scanning
- Vulnerability identification
- Exploitation with Metasploit
- Linux privilege escalation basics

## Disclaimer
This was performed in a legal, isolated lab environment against a machine 
intentionally designed for security training purposes.
