# DVD Rental Data Generator

## Setup Instructions

1. **Clone Repository**
```bash
git clone https://github.com/agogodavid/dvdrental_live.git
cd dvdrental_live
```

2. **Create Virtual Environment**
```bash
python3 -m venv dvdrental_live
source dvdrental_live/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Database (Optional)**
```bash
# Set custom database name (default: dvdrental_live)
export DATABASE_NAME=my_custom_db
```

5. **Run Setup Script**
```bash
bash setup.sh
```

## Configuration Options

- **Database Name**: Set via `DATABASE_NAME` environment variable
- **MySQL Credentials**: Configure in `config.json`
- **Simulation Parameters**: Adjust in `config.json` (start date, initial weeks, etc.)

## Environment Variables

| Variable          | Description                          | Default Value       |
|-------------------|--------------------------------------|---------------------|
| `DATABASE_NAME`   | Target database name                 | `dvdrental_live`    |
| `MYSQL_HOST`      | MySQL server host                    | `localhost`         |
| `MYSQL_USER`      | MySQL username                       | `root`              |
| `MYSQL_PASSWORD`  | MySQL password                       | `root`              |

## Custom Configuration

For advanced configuration, modify `config.json`:
```json
{
  "mysql": {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "dvdrental_live"
  },
  "simulation": {
    "start_date": "2001-10-01",
    "initial_weeks": 12
  }
}
```

## Usage

**Initial Setup**:
```bash
# With default database
python generator.py

# With custom database
python generator.py --database my_custom_db
```

**Incremental Updates**:
```bash
# Add 4 weeks to default database
python incremental_update.py 4

# Add 4 weeks to custom database
python incremental_update.py 4 --database my_custom_db

# With seasonal drift (50% increase)
python incremental_update.py 4 --seasonal 50 --database my_custom_db
```

## Features

- Database creation with schema
- Realistic transaction patterns
- Seasonal demand fluctuations
- Customer lifecycle simulation
- Inventory management
- Payment tracking

## Troubleshooting

1. **Database Connection Errors**:
   - Verify MySQL server is running
   - Check credentials in `config.json`
   - Ensure MySQL user has CREATE/DROP privileges

2. **Missing Dependencies**:
   - Run `pip install -r requirements.txt`

3. **Permission Issues**:
   - Use `sudo` if needed for system-wide installations
   - Verify file permissions for `schema.sql`