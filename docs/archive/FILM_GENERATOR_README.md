# Film Generator Module

## Overview

The Film Generator module is a separate Python file that handles the generation of new films for quarterly releases. It reads source details from separate .txt files for easy expansion of movie titles and stores film release information in a dedicated database table.

## Features

1. **Separate Film Generation Logic**: Isolated in `film_generator.py`
2. **Template-Based Title Generation**: Reads from `.txt` files for easy expansion
3. **Quarterly Film Releases**: Generates films every quarter and tracks releases
4. **Employee-Linked Purchasing**: Links inventory purchases to specific employees
5. **Database Integration**: Stores release information in `film_releases` table

## File Structure

```
film_generator.py          # Main film generator module
film_templates/            # Directory containing template files
  ├── action.txt           # Action film title templates
  ├── comedy.txt           # Comedy film title templates
  ├── drama.txt            # Drama film title templates
  ├── horror.txt           # Horror film title templates
  └── romance.txt          # Romance film title templates
```

## Database Schema

The module creates two tables:

1. `film_releases` table for tracking movie market releases:
```sql
CREATE TABLE film_releases (
    release_id INT AUTO_INCREMENT PRIMARY KEY,
    film_id INT NOT NULL,
    release_quarter VARCHAR(10) NOT NULL,
    release_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (film_id) REFERENCES film(film_id),
    INDEX idx_release_quarter (release_quarter),
    INDEX idx_release_date (release_date)
);
```

2. `inventory_purchases` table for tracking inventory ordering:
```sql
CREATE TABLE inventory_purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    film_id INT NOT NULL,
    inventory_id INT,
    staff_id INT,
    purchase_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (film_id) REFERENCES film(film_id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id),
    INDEX idx_film_id (film_id),
    INDEX idx_staff_id (staff_id),
    INDEX idx_purchase_date (purchase_date)
);
```

## Usage

### Generating Films

```python
from film_generator import FilmGenerator

# Initialize with MySQL configuration
film_gen = FilmGenerator(mysql_config)

# Generate films for a specific quarter
films_added = film_gen.generate_quarterly_films(
    quarter="Q1 2023",
    num_films=5,
    category_focus="Action"
)
```

### Adding Film Batches

```python
# Add a batch of films with specific release date
films_added = film_gen.add_film_batch(
    num_films=3,
    category_focus="Comedy",
    description="Summer comedy releases",
    release_date=date(2023, 6, 15)
)
```

## Template Files

Template files are simple text files with one title template per line. Placeholders are used to generate varied titles:

- `{adjective}` - Adjective placeholder
- `{noun}` - Noun placeholder
- `{name}` - Name placeholder
- `{location}` - Location placeholder
- `{verb}` - Verb placeholder

### Example Template (action.txt)
```
The {adjective} Mission
Operation {name}
{adjective} Strike
The {name} Protocol
```

## Integration with Master Simulation

The film generator is integrated with `master_simulation.py` to automatically generate films during quarterly releases as defined in the `FILM_RELEASES` schedule.

## Testing

Run the test suite to verify functionality:

```bash
python test_film_generator.py
```

## Extending Templates

To add new film categories:
1. Create a new `.txt` file in `film_templates/` directory
2. Name it after the category (e.g., `sci-fi.txt`)
3. Add title templates with appropriate placeholders
4. The system will automatically load and use the new templates

## Employee Linking

Each film release is linked to a staff member who made the purchasing decision, allowing for long-term profitability analysis of inventory purchases by employee.