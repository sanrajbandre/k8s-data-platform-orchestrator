# Ansible Deployment (Rocky Linux 9.x)

This directory contains automation for:
- full install + deploy of the platform on Rocky Linux 9.x
- maintenance restarts (entire app or scoped components)

## Files
- `playbooks/site.yml`: full deployment playbook
- `playbooks/maintenance.yml`: restart operations
- `inventory/hosts.ini.example`: inventory example
- `group_vars/all.yml.example`: deployment variables
- `requirements.yml`: Ansible collections

## Prerequisites
- Control machine with `ansible-core` installed
- SSH access to Rocky 9 host(s) with sudo

## Setup
1. Copy inventory and vars:
```bash
cd deploy/ansible
cp inventory/hosts.ini.example inventory/hosts.ini
cp group_vars/all.yml.example group_vars/all.yml
```

2. Edit `group_vars/all.yml`:
- `repo_url`
- `mysql_app_password`
- `jwt_secret`
- `fernet_key`
- any webhook/email/OpenAI settings you need

3. Install required collection:
```bash
ansible-galaxy collection install -r requirements.yml
```

## Full deployment
```bash
ansible-playbook playbooks/site.yml
```

## Maintenance restart operations
Restart entire application stack:
```bash
ansible-playbook playbooks/maintenance.yml -e restart_target=all
```

Restart backend only:
```bash
ansible-playbook playbooks/maintenance.yml -e restart_target=backend
```

Restart frontend only (nginx static serving layer):
```bash
ansible-playbook playbooks/maintenance.yml -e restart_target=frontend
```

Restart worker services only:
```bash
ansible-playbook playbooks/maintenance.yml -e restart_target=worker
```

## Backend restart behavior
By default backend restart only restarts `orchestrator-backend`.
If you also want worker+beat restarted when targeting backend, set:
```yaml
include_worker_with_backend_restart: true
```
in `group_vars/all.yml`.
