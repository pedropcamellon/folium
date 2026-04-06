# Grafana Dashboard Provisioning

## How It Works

Grafana automatically loads dashboards from this directory via the provisioning system.

## Adding New Dashboards

### Method 1: Export from Grafana UI (Recommended)

1. Create/edit dashboard in Grafana UI (http://localhost:3001)
2. Click **Share** (top right) → **Export**
3. Enable **Export for sharing externally**
4. Click **Save to file**
5. Save JSON file to this directory
6. Restart Grafana: `docker compose restart southdrift-grafana`

### Method 2: Copy From Grafana Community

1. Browse https://grafana.com/grafana/dashboards/
2. Download JSON for dashboard
3. Save to this directory
4. Adjust datasource UID if needed:

   ```json
   "datasource": {
     "type": "prometheus",
     "uid": "prometheus"
   }
   ```

### Method 3: Create From Scratch

Use existing JSON files as templates. Key structure:

```json
{
  "title": "My Dashboard",
  "panels": [...],
  "templating": {...},
  "time": {...}
}
```

## Folder Organization

Dashboards are automatically placed in the **SouthDrift** folder in Grafana.

Configure in `dashboard.yml`:

```yaml
providers:
  - name: "Default"
    folder: "SouthDrift" # Change folder name here
```

## Settings

- **Auto-reload**: Every 10 seconds (`updateIntervalSeconds: 10`)
- **UI Edits**: Allowed (`allowUiUpdates: true`)
- **Deletion**: Allowed (`disableDeletion: false`)

## Tips

- Keep one dashboard per JSON file
- Use descriptive filenames: `temporal-workflows.json`, `api-performance.json`
- Add comments in this README for complex dashboards
- Version control tracks all changes automatically
