# Unrecorded Rental Returns Analysis

## Problem Statement

Your DVD rental simulation contains **14,000+ rentals with NULL return_date values**. This creates a critical data quality issue:

- **Missing business data**: No payment records (can't bill customers)
- **Inventory discrepancy**: System thinks items are still checked out indefinitely
- **Analytical problems**: Revenue, profitability, and customer metrics are incomplete
- **Operational risk**: Broken business processes if this data were real

## Root Cause

The simulation generates rentals without corresponding return transactions. This is likely because:

1. **Batch processing issue**: Rentals created but return processing never completed
2. **Timing bug**: Rentals created in one phase but returns handled in another
3. **Data generation incomplete**: Transaction generation creates rentals without matching returns

## The Challenge

Simply fixing the NULL values breaks **data integrity** if done incorrectly. We must:

- ✅ Maintain immutable operational records (audit trail)
- ✅ Fix analytical/reporting layer without altering source data
- ✅ Enable business analysis despite incomplete data
- ✅ Document the data quality issue for stakeholders

## Contents of This Folder

- **analysis.py** - Diagnose the issue with detailed reporting
- **solutions.md** - Compare four different approaches with tradeoffs
- **data_integrity_principles.md** - Why operational integrity matters
- **fix_analytical_view.sql** - RECOMMENDED: Fix at analytical layer only
- **fix_operational_direct.sql** - WARNING: What NOT to do (and why)
- **implementation_guide.md** - Step-by-step safe implementation

## Quick Start

```bash
# 1. Analyze the problem
python analysis.py

# 2. Review the implications
less solutions.md

# 3. Understand why integrity matters
less data_integrity_principles.md

# 4. Implement analytical fix (safe)
mysql -u root -p < fix_analytical_view.sql

# 5. Query clean analytical data
SELECT * FROM vw_rentals_with_estimated_returns;
```

## Key Insight

**Don't modify the operational rental table.** Instead, create a **parallel analytical layer** that intelligently handles the missing data for reporting purposes while preserving the original record.
