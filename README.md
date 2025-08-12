## Practice Assessments (multi-problem)

Minimal framework to develop and test multiple practice problems.

### Setup
- Install Python packages:
```bash
pip install -r requirements.txt
```

### Structure
```text
CS/
  practice_assessments/
    run_practice.py          # problem selector and test runner
    file_storage/            # example problem
      simulation.py          # implement your solution here
      levels/                # problem specification by level
        level1.md
        level2.md
        level3.md
        level4.md
      tests/                 # unit tests per level
        test_level1.py
        test_level2.py
        test_level3.py
        test_level4.py
  requirements.txt
  README.md
```

### List and run problems
- List available problems:
```bash
python practice_assessments/run_practice.py --list
```
- Run a specific problem (example: `file_storage`):
```bash
python practice_assessments/run_practice.py --problem file_storage
```
Optional flags:
```bash
python practice_assessments/run_practice.py --problem file_storage --pattern 'test_*.py' --fail-fast
```

### Add a new problem
1. Create `practice_assessments/<problem_name>/`.
2. Add your solution file `simulation.py` there.
3. Add tests under `practice_assessments/<problem_name>/tests/` named `test_*.py` that import local modules directly (e.g., `from simulation import ...`).
4. Optionally add specs in `practice_assessments/<problem_name>/levels/`.
5. Run it:
```bash
python practice_assessments/run_practice.py --problem <problem_name>
```

## Practice Assessments (multi-problem)

Minimal framework to develop and test multiple practice problems.

### Setup
- Install Python packages:
```bash
pip install -r requirements.txt
```

### Structure
```text
CS/
  practice_assessments/
    run_practice.py          # problem selector and test runner
    file_storage/            # example problem
      simulation.py
      test_simulation.py
      level1.md
      level2.md
      level3.md
      level4.md
  requirements.txt
  Readme.md
```

### List and run problems
- List available problems:
```bash
python practice_assessments/run_practice.py --list
```
- Run a specific problem (example: `file_storage`):
```bash
python practice_assessments/run_practice.py --problem file_storage
```
Optional:
```bash
# custom discovery pattern or stop on first failure
python practice_assessments/run_practice.py --problem file_storage --pattern 'test_*.py' --fail-fast
```

### Add a new problem
1. Create `practice_assessments/<problem_name>/`.
2. Add your solution files (e.g., `simulation.py`).
3. Add tests named `test_*.py` that import local modules directly (e.g., `from simulation import ...`).
4. Run it:
```bash
python practice_assessments/run_practice.py --problem <problem_name>
```

