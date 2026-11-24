# SQL & PL/SQL Coding Standards

## File Naming Conventions

| File Type                              | Extension |
| -------------------------------------- | --------- |
| Package spec (and optionally body)     | `.pkg`    |
| Package body                           | `.pkb`    |
| Procedure                              | `.prc`    |
| Function                               | `.fnc`    |
| Object type spec (and optionally body) | `.typ`    |
| Object type body                       | `.tyb`    |
| Stored Java procedure                  | `.sjp`    |
| Stored Java function                   | `.sjf`    |
| Trigger                                | `.trg`    |
| Other PL/SQL                           | `.pls`    |
| Other SQL                              | `.sql`    |

**Rules:**

- Maintain code in text files — not via TOAD/SQL Developer direct edit. Enables version control.
- Package spec and body in **separate files** — minimises invalidation when body changes.

## Identifier Naming Conventions

Identifiers follow the pattern: `<Scope><Type><PrimaryIdentifier><Modifier><Suffix>`

Only **Scope** and **PrimaryIdentifier** are mandatory.
Use the **minimum** that is still unambiguous. Do not burden names with redundant metadata obtainable from context.

### Scope Prefixes

| Prefix | Meaning                            |
| ------ | ---------------------------------- |
| `g_`   | Global (package-level) variable    |
| `l_`   | Local variable (within subprogram) |
| `p_`   | Parameter                          |

### Type Prefixes

| Prefix | Type                   | Example          |
| ------ | ---------------------- | ---------------- |
| `k_`   | Constant               | `k_mailhost`     |
| `g_`   | Package-level variable | `g_loop_count`   |
| `l_`   | Local variable         | `l_loop_count`   |
| `c_`   | Cursor                 | `c_employees`    |
| `cp_`  | Cursor parameter       | `cp_employee_id` |
| `r_`   | Record                 | `r_employee`     |

### Parameter Suffixes (OUT/INOUT only; IN is default and needs no suffix)

| Suffix   | Direction |
| -------- | --------- |
| _(none)_ | `IN`      |
| `_out`   | `OUT`     |
| `_inout` | `IN OUT`  |

### Private Subprogram Suffix

All functions and procedures declared **only in the package body** (i.e. not exposed in the spec) must have a trailing underscore (`_`) appended to the name:

```sql
-- Public (declared in spec and body)
FUNCTION get_account_balance(p_account_id accounts.account_id%TYPE) RETURN NUMBER;

-- Private (body only)
FUNCTION get_account_balance_(p_account_id accounts.account_id%TYPE) RETURN NUMBER;
PROCEDURE validate_credit_(p_account_id accounts.account_id%TYPE);
```

**Rules:**

- The trailing `_` is the sole distinguishing marker — do not add any other prefix or suffix to signal privacy.
- Forward declarations (local module stubs at the top of the body) must also carry the `_` suffix, since they exist only to resolve forward references among private subprograms.
- Never apply the `_` suffix to public subprograms, package-level variables, constants, types, or exceptions — only to private functions and procedures.

### Naming Rules

- **Primary identifier is paramount.** All prefixes/suffixes are secondary.
- No random abbreviations. If `flgtdt` isn't obviously `flight_date`, don't use it.
- If a name feels too long, think harder — don't truncate vowels. `ODI_LOE_BY_AC_PD_L1` is not acceptable.
- Use plurals for cursors and collections (they represent sets); use singular for records.
- Never name a cursor `c1`. If you're numbering cursors, you haven't named them.

## Specific Identifier Patterns

### Cursors

```sql
-- Named after the table/view being processed, plural
c_customers
c_new_accounts

-- Ref cursor passed as parameter
pc_old_accounts  -- or p_old_accounts is acceptable
```

### Records

```sql
lr_account        -- formal local record
r_account         -- informal
pr_account        -- parameter record
gr_last_account   -- global record
r_new_account     -- with modifier
```

### Loop Index

```sql
FOR i IN 1..12 LOOP          -- acceptable for simple loops
FOR i_month IN 1..12 LOOP    -- more descriptive
FOR r IN c_discrepancies LOOP
FOR r_emp IN c_emp LOOP
```

Never use `r1` — use a descriptive name.

### Collection Type

Use `_tt` suffix for collection ("table") types:

```sql
TYPE account_tt IS TABLE OF accounts%ROWTYPE;
l_accounts account_tt;
l_new_accounts account_tt;
l_old_accounts account_tt;
```

Distinguish collection subtypes only when necessary:

- `_aatt` — associative array
- `_vatt` — varray
- `_ntt` — nested table
- `_tt` — generic (use this unless distinction matters)

### PL/SQL Record Type

```sql
TYPE g_address_rectype IS RECORD (...);  -- formal
TYPE address_rectype IS RECORD (...);    -- informal
TYPE address IS RECORD (...);            -- acceptable when unambiguous
```

### Schema-Level Object Type

Use `_ot` suffix:

```sql
CREATE OR REPLACE TYPE customer_ot AS OBJECT (...);
```

### Schema-Level Collection Type

Define generic reusable types:

```sql
CREATE OR REPLACE TYPE number_tt    AS TABLE OF NUMBER(38,10);
CREATE OR REPLACE TYPE integer_tt   AS TABLE OF INTEGER;
CREATE OR REPLACE TYPE date_tt      AS TABLE OF DATE;
CREATE OR REPLACE TYPE varchar2_tt  AS TABLE OF VARCHAR2(4000);
CREATE OR REPLACE TYPE timestamp_tt AS TABLE OF TIMESTAMP;
```

## Package Structure

A package consists of two files: the spec (`.pkg`) and the body (`.pkb`). Structure both files in the fixed section order below. Never reorder sections.

### Package Spec

```sql
CREATE OR REPLACE
PACKAGE my_package IS

------------
--  OVERVIEW
--
--  One paragraph describing what this package does and why it exists.
--

-----------
--  EXAMPLE
--
--  Minimal runnable usage example.
--

-------------
--  RESOURCES
--
--  Links to design docs, tickets, related packages.
--

----------------------------------------------------------
--	GLOBAL PUBLIC EXCEPTIONS
----------------------------------------------------------

----------------------------------------------------------
--	GLOBAL PUBLIC TYPES
----------------------------------------------------------

----------------------------------------------------------
--	GLOBAL PUBLIC CONSTANTS
----------------------------------------------------------

----------------------------------------------------------
--	GLOBAL PUBLIC MODULES
----------------------------------------------------------

/**
*	One-line description.
*	@param p_parameter  description
*	@return             description
*/
FUNCTION my_public(p_parameter IN VARCHAR2) RETURN VARCHAR2;

END my_package;
/
```

**Rules:**

- Every package spec must open with OVERVIEW, EXAMPLE, and RESOURCES comment blocks.
- Public subprograms must be documented with JSDoc-style block comments (`/** ... */`) immediately above the signature — one `@param` line per parameter, one `@return` line.
- Sections appear in the order shown; omit a section's content if empty but keep the header.

### Package Body

```sql
CREATE OR REPLACE
PACKAGE BODY my_package IS

----------------------------------------------------------
--	PRIVATE EXCEPTIONS
----------------------------------------------------------

----------------------------------------------------------
--	PRIVATE TYPES
----------------------------------------------------------

----------------------------------------------------------
--	PRIVATE CONSTANTS
----------------------------------------------------------

----------------------------------------------------------
--	PRIVATE VARIABLES
----------------------------------------------------------

----------------------------------------------------------
--	LOCAL MODULES
----------------------------------------------------------

-- Forward declarations: only needed when a private subprogram
-- is called before its full definition appears in this file.
FUNCTION my_private_(p_parameter IN VARCHAR2) RETURN VARCHAR2;

----------------------------------------------------------
--	GLOBAL MODULES
----------------------------------------------------------

/*
*	Implementation of public subprograms first,
*	then full definitions of private subprograms.
*/
FUNCTION my_public(p_parameter IN VARCHAR2) RETURN VARCHAR2
IS
BEGIN
	RETURN my_private_(p_parameter => p_parameter);
END my_public;


FUNCTION my_private_(p_parameter IN VARCHAR2) RETURN VARCHAR2
IS
BEGIN
	RETURN p_parameter;
END my_private_;

END my_package;
/
```

**Rules:**

- Section order is fixed: private exceptions → private types → private constants → private variables → local modules → global modules.
- LOCAL MODULES contains only forward declarations (stubs). Full implementations go in GLOBAL MODULES.
- Add a forward declaration only when required to resolve a forward reference — do not declare all private subprograms upfront as a matter of habit.
- Within GLOBAL MODULES, place public subprogram implementations first, private implementations after. This makes the public interface immediately visible when reading the body.
- Use `/*  */` block comments (not JSDoc) for implementation notes inside the body; JSDoc belongs only on the spec signatures.
- The `END <subprogram_name>;` label is mandatory on every subprogram — match the name exactly, including the trailing `_` for private subprograms.

### Standalone Procedure/Function Structure

For standalone `.prc` / `.fnc` files the same section discipline applies, collapsed into a single unit:

```sql
CREATE OR REPLACE
PROCEDURE my_procedure
    ( p_account_id  accounts.account_id%TYPE
    , p_result_out  VARCHAR2 )
IS
	-- constants
	k_max_retries CONSTANT pls_integer := 3;

	-- types

	-- variables
	l_attempt pls_integer := 0;

	-- cursors

	-- local (private) subprograms
	PROCEDURE validate_(p_id IN accounts.account_id%TYPE) IS
	BEGIN
		...
	END validate_;

BEGIN
	...
END my_procedure;
/
```

**Rules:**

- Declaration block order: constants → types → variables → cursors → local subprograms.
- Local subprograms within a standalone unit also follow the trailing `_` private naming convention.
- No section-header comments are required in standalone units — the declaration block is small enough to read without them. Add them only if the declaration block exceeds ~30 lines.

## Code Formatting

### Core Principle

> Format to show **logical structure**. Not for aesthetics. Structure should be visible — if it looks bad, that's information.

### Indentation

- Use **tabs**, not spaces.
- Left-align blocks to create a clear vertical line at each level.

### Case Convention

Uppercase SQL and PL/SQL keywords; lowercase all other code tokens.
Preserve case in quoted identifiers and string literals.

### Procedure/Function Declarations

First parameter on new line; one parameter per line; closing paren on last parameter line:

```sql
FUNCTION invoice_address
    ( p_account_id  accounts.account_id%TYPE
    , p_date        DATE )
    RETURN address;

PROCEDURE do_stuff_rather_long_name
    ( p_first_parameter   BOOLEAN DEFAULT FALSE
    , p_second_parameter  service_agreement.agreement_status%TYPE DEFAULT 2
    , p_third_parameter   currency_amount DEFAULT 0 );
```

### Variable Assignments

One statement per line. Space around operators:

```sql
-- Bad
l_firstname := 'Dimitri'; l_lastname := 'Papadopoulos';
l_firstname:='Dimitri';

-- Good
l_firstname := 'Dimitri';
l_lastname  := 'Papadopoulos';

-- Preferred: assign at declaration
l_firstname employees.firstname%TYPE := 'Dimitri';
```

### Multi-Line Statements

Indent continuation lines. Each parameter on its own line when formal layout is required:

```sql
upload_sales
( p_company_id
, p_last_year_date
, p_rollup_type
, p_total );
```

## Commenting Style

### Rules

- **Comment as you code** — not after.
- **Explain why, not how.** Don't document what the code plainly says.
- Use `--` line comments, not `/* ... */` blocks — easier to comment out sections when debugging.
- Indent comments at the same level as the code they describe.
- No decorative ASCII art. It creates maintenance burden.

```sql
-- Bad
/*********************************************************/
/* Delete all the customers and fire the employees.      */
/*********************************************************/

-- Good
-- Delete all customers and fire all employees:
```

## PL/SQL Programming Guidelines

### Conditional Statements

Brackets are optional — PL/SQL has `THEN` to terminate conditions:

```sql
-- Bad
IF ((x = 1) AND (y = 2)) THEN

-- Good
IF (x = 1) THEN
IF x = 1 THEN
IF x = 1 AND y = 2 THEN
IF (x = 1 AND y = 2) THEN
```

Boolean operators (`AND`/`OR`) go at the **start** of the line, not end:

```sql
-- Bad
IF to_char(SYSDATE,'D') > 1 AND
   mypackage.myprocedure(1,2,3,4) NOT BETWEEN 1 AND 99 THEN

-- Good
IF to_char(SYSDATE,'D') > 1
AND mypackage.myprocedure(1,2,3,4) NOT BETWEEN 1 AND 99
THEN
```

Mixed OR/AND — align bracketed conditions vertically:

```sql
IF a = 1
AND (   b = 2
     OR c = 3
     OR d = 4 )
THEN
```

### Loops

- `FOR`/`WHILE` loops should not use explicit `EXIT` — use them when you know the iteration count.
- **Cursor FOR loop** is preferred over `OPEN-FETCH-EXIT-CLOSE` in nearly all cases.
- Anonymous cursor FOR loops are acceptable:

```sql
FOR r IN (
    SELECT e.employee_id, e.first_name
    FROM   employees e
    ORDER BY 1
)
LOOP
    ...
END LOOP;
```

Use `OPEN-FETCH-EXIT-CLOSE` only when:

- Working with a weak ref cursor (runtime-typed).
- You need to retain the record after loop completion (rare).

### Booleans

Use boolean expressions directly — do not use IF to assign TRUE/FALSE:

```sql
-- Bad
IF hiredate < SYSDATE THEN
    date_in_past := TRUE;
ELSE
    date_in_past := FALSE;
END IF;

-- Good
date_in_past := hiredate < SYSDATE;

-- Bad (function return)
IF total_sal > 10000 THEN
    RETURN TRUE;
ELSE
    RETURN FALSE;
END IF;

-- Good
RETURN total_sal > 10000;
```

Use boolean variables to name complex conditions:

```sql
eligible_for_raise :=
    total_sal BETWEEN 10000 AND 50000
    AND emp_status(emp_rec.empno) = 'N'
    AND months_between(emp_rec.hiredate, SYSDATE) > 10;

IF eligible_for_raise THEN
    give_raise(emp_rec.empno);
END IF;
```

### Prefer SQL Over PL/SQL

SQL is almost always faster. Replace PL/SQL loops with single SQL statements when possible:

```sql
-- Bad: 20 INSERT statements
FOR i_year IN 1..20 LOOP
    INSERT INTO table1
    SELECT * FROM table2
    WHERE  starting_year = i_year;
END LOOP;

-- Good: 1 INSERT statement
INSERT INTO table1
SELECT * FROM table2
WHERE  starting_year BETWEEN 1 AND 20;
```

### Constants

- No magic numbers or literals in code. Declare named constants (`k_` prefix).
- Each constant defined in exactly one place.
- If a variable never changes, convert it to a constant.

```sql
k_ship_express  CONSTANT VARCHAR2(10) := 'EXPRESS';
k_ship_standard CONSTANT VARCHAR2(10) := 'STANDARD';
```

### Variable Discipline

- One variable, one purpose. Never reuse a variable for two different things.
- Remove unused variables. Use PL/SQL compile-time warnings and PL/Scope to detect them.

### Use `%TYPE`

Always anchor variable types to column definitions:

```sql
-- Bad
PROCEDURE format_customer ( p_customer_id INTEGER )
IS
    l_first_name  VARCHAR2(30);
    l_last_name   VARCHAR2(30);

-- Good
PROCEDURE format_customer ( p_customer_id customers.cst_id%TYPE )
IS
    l_first_name  customers.cst_first_name%TYPE;
    l_last_name   customers.cst_last_name%TYPE;
```

Benefits: stays in sync with schema changes; self-documents the relationship to DB columns.

### Use `%ROWTYPE` for Records

```sql
r_employee employees%ROWTYPE;
```

### Subtypes

Create subtypes to document business intent, not technical detail:

```sql
-- Bad subtype (just adds noise)
SUBTYPE emp240_rtyp IS c_emp240%ROWTYPE;

-- Good subtype (documents business concept)
SUBTYPE money IS stock_items.unit_price%TYPE;
SUBTYPE room_number IS rooms.room_number%TYPE;
```

Consider a dedicated package containing only standard subtypes, constants, and variable declarations.

## Exception Handling

### Prefer `raise_application_error` Over Named Exceptions

Named exceptions carry no explanatory message:

```sql
-- Bad: no diagnostic info
RAISE errorpkg.fatal_error;

-- Good: stack trace + context
raise_application_error
( errorpkg.k_fatal_error
, 'Credit check failed for account ' || r_acc.acc_id
, TRUE );
```

### Error Code Strategy

For most applications, one error code per package (or even one for the whole application) is sufficient:

```sql
k_error_code CONSTANT pls_integer := -20042;
```

Then use `k_error_code` in all `raise_application_error` calls within that package.

### Log and Raise Pattern

```sql
-- Log and raise in one call via utility procedure:
l_error_text := 'Invalid account ' || r_acc.acc_id;
error_pkg.log_and_raise(errorpkg.k_invalid_account, l_error_text);
```

Only log at the topmost error-handling level; propagate via `raise_application_error` with `TRUE` (preserve stack).

### Keep It Simple

Avoid a proliferation of application-specific named exceptions that callers have to test for. The calling procedure usually doesn't care _why_ the callee failed — it just failed. Put cleanup logic inside the procedure that fails, not in every caller.

## SQL Layout Guidelines

### Left-Align Everything

Use the same left-alignment rules as PL/SQL. The "right-gutter" alignment style is rejected:

```sql
-- Bad (right-gutter)
SELECT last_name, first_name
  FROM employees
 WHERE department_id = 15
   AND hire_date < SYSDATE;

-- Good (left-aligned)
SELECT last_name, first_name
FROM   employees
WHERE  department_id = 15
AND    hire_date < SYSDATE;
```

### One Expression Per Line

```sql
SELECT e.last_name
     , c.name
     , max(sh.salary) best_salary_ever
FROM   employees e
       JOIN companies c
            ON  c.company_id = e.company_id
       JOIN salary_history sh
            ON  sh.employee_id = e.employee_id
WHERE  e.hire_date > add_months(SYSDATE, -60)
AND    EXISTS
       ( SELECT 1
         FROM   some_other_table ot
         WHERE  ot.employee_id = e.employee_id )
GROUP BY e.last_name, c.name
ORDER BY e.last_name, c.name;
```

### INSERT Column List

```sql
INSERT INTO employees
( emp_id
, emp_firstname
, emp_lastname )
VALUES
( emp_seq.nextval
, r_emp.firstname
, r_emp.lastname );
```

### UPDATE

```sql
UPDATE employees
SET    salary = salary * l_raise_factor
WHERE  department_id = l_department_id
AND    termination_date IS NULL;
```

### Blank Lines

- Max **one** blank line within a subprogram body.
- **Two** blank lines between subprograms in a package or type body.

### Table Aliases

Use **meaningful abbreviations** based on the table name — not `a`, `b`, `c`:

```sql
-- Bad
FROM employees a JOIN companies b ON b.com_id = a.emp_com_id

-- Good
FROM employees emp JOIN companies com ON com.com_id = emp.emp_com_id
```

Consistent alias length (e.g. 3 chars) is fine; clarity is the goal.

### ANSI Join Syntax

Use explicit `JOIN ... ON` syntax. Implicit comma joins are not acceptable:

```sql
-- Bad (implicit join)
FROM employees e, departments d
WHERE d.department_id = e.department_id

-- Good (ANSI)
FROM employees e
     JOIN departments d
          ON  d.department_id = e.department_id
```

Two spaces after `ON` so that `AND` conditions align with the `ON` column:

```sql
JOIN departments d
     ON  d.department_id = e.department_id
     AND d.active_flag = 'Y'
```

Join conditions should flow in the same left-to-right order as the FROM clause.

## Summary: The Two Non-Negotiables

If nothing else, enforce these:

1. **Give everything meaningful names.**
2. **If anything is not obvious, change it so it is — and if you can't, explain it with a comment.**
