import paramiko
import os
import requests

# List of servers
servers = ["172.28.40.18" "172.28.40.38" "172.28.40.43"]

# Define output directory
output_dir = "reports"
os.makedirs(output_dir, exist_ok=True)

# SSH credentials
username = "afernandez"
ssh_key_path = "/root/.ssh/id_rsa"  # Update with your SSH private key path

# Function to run commands on a remote server via SSH
def run_ssh_command(server, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(server, username=username, key_filename=ssh_key_path)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        ssh.close()
        return output
    except Exception as e:
        print(f"Failed to run command on {server}: {e}")
        return ""

# Loop through each server
for server in servers:
    print(f"Running script on {server}...")

    # Define output file for each server
    output_file = os.path.join(output_dir, f"{server}_system_report.txt")

    # Run commands on the server
    hostname = run_ssh_command(server, "hostname").strip()
    ip_address = run_ssh_command(server, "hostname -I | awk '{print $1}'").strip()
    uptime_info = run_ssh_command(server, "uptime -p").strip()
    processors = run_ssh_command(server, "nproc").strip()
    memory = run_ssh_command(server, "free -h | grep Mem | awk '{print $2}'").strip()
    local_filesystems = run_ssh_command(server, "df -h | grep -vE 'tmpfs|devtmpfs|nfs|cifs'").strip()
    nfs_cifs = run_ssh_command(server, "df -h | grep -E 'nfs|cifs'").strip()
    firewall_active = run_ssh_command(server, "systemctl is-active firewalld").strip()
    iptables_active = run_ssh_command(server, "systemctl is-active iptables").strip()
    fstab_content = run_ssh_command(server, "cat /etc/fstab").strip()
    passwd_content = run_ssh_command(server, "cat /etc/passwd").strip()
    crontab_jobs = run_ssh_command(server, "crontab -l").strip()
    active_services = run_ssh_command(server, "systemctl list-units --type=service --state=active").strip()
    top_processes = run_ssh_command(server, "ps aux --sort=-%mem | head -n 8").strip()
    last_users = run_ssh_command(server, "last -n 7").strip()
    patch_date = run_ssh_command(server, "rpm -q --last kernel | head -n 1").strip()
    updated_packages = run_ssh_command(server, f"rpm -qa --last | grep '{patch_date.split()[2]} {patch_date.split()[3]} {patch_date.split()[4]}'").strip()

    # Check firewall rules if active
    if firewall_active == "active":
        firewall_rules = run_ssh_command(server, "sudo firewall-cmd --list-all").strip()
        with open(f"firewall_rules_{server}.txt", "w") as file:
            file.write(firewall_rules)

    # Check iptables rules if active
    if iptables_active == "active":
        iptables_rules = run_ssh_command(server, "sudo iptables -S").strip()
        with open(f"iptables_rules_{server}.txt", "w") as file:
            file.write(iptables_rules)

    # Create the output file with formatted content
    with open(output_file, "w") as file:
        file.write(f"Hostname: {hostname}\n")
        file.write(f"IP Address: {ip_address}\n")
        file.write(f"Uptime: {uptime_info}\n")
        file.write(f"Processors: {processors}\n")
        file.write(f"Memory: {memory}\n")
        file.write("Local Filesystems:\n")
        file.write(f"{local_filesystems}\n")
        file.write("NFS or CIFS Filesystems:\n")
        file.write(f"{nfs_cifs}\n")
        file.write(f"Firewall Active: {firewall_active}\n")
        if firewall_active == "active":
            file.write(f"Firewall rules saved to firewall_rules_{server}.txt\n")
        file.write(f"iptables Active: {iptables_active}\n")
        if iptables_active == "active":
            file.write(f"iptables rules saved to iptables_rules_{server}.txt\n")
        file.write("fstab Content:\n")
        file.write(f"{fstab_content}\n")
        file.write("passwd Content:\n")
        file.write(f"{passwd_content}\n")
        file.write("Crontab Jobs:\n")
        file.write(f"{crontab_jobs}\n")
        file.write("Active Services:\n")
        file.write(f"{active_services}\n")
        file.write("Top 7 Memory Consuming Processes:\n")
        file.write(f"{top_processes}\n")
        file.write("Last 7 Users:\n")
        file.write(f"{last_users}\n")
        file.write(f"System Last Patched On: {patch_date}\n")
        file.write("Updated Packages Last Patch:\n")
        file.write(f"{updated_packages}\n")

# Send the reports to Slack
# Note: Replace YOUR_SLACK_WEBHOOK_URL with your actual Slack webhook URL
for server in servers:
    output_file = os.path.join(output_dir, f"{server}_system_report.txt")
    with open(output_file, "r") as file:
        report_content = file.read()
    response = requests.post(
        "YOUR_SLACK_WEBHOOK_URL",
        headers={"Content-type": "application/json"},
        json={"text": report_content}
    )
    print(f"Sent report for {server}, response status: {response.status_code}")
