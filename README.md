
# Efficient Chess AI Agent

This repository contains the implementation of an efficient chess-playing AI agent designed for the **FIDE & Google Efficient Chess AI Challenge**. The primary goal is to develop a highly efficient and strategic agent capable of operating under strict computational constraints.

---

## Project Goals

1. **Resource Efficiency**:
   - Operate within the competition's strict limits of **5 MiB RAM**, a **single 2.20 GHz core**, and a **64 KiB submission size**.
2. **Strategic Play**:
   - Leverage advanced chess strategies with minimal resources.
3. **Scalable Architecture**:
   - Provide a framework for experimentation and performance improvement.

---

## Features

- **Alpha-Beta Pruning**:
  - Optimized search algorithm to explore game trees efficiently.
- **Quiescence Search**:
  - Enhances tactical accuracy by extending evaluations during critical positions.
- **Iterative Deepening**:
  - Combines depth-first search with time management for better performance.
- **Move Ordering**:
  - Uses MVV-LVA (Most Valuable Victim - Least Valuable Attacker) heuristic for efficient move prioritization.
- **FEN Parsing**:
  - Supports accurate board state representation and evaluation.

---

## Repository Structure

```plaintext
.
├── bot.py               # Main implementation of the chess bot
├── environment.ipynb    # Notebook for environment setup and experimentation
├── README.md            # Documentation
├── requirements.txt     # Python dependencies
└── LICENSE              # License for the project
```

---

## Setup

### Prerequisites

- **Python 3.6 or higher**
- `pip` for managing dependencies

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/efficient-chess-ai.git
   cd efficient-chess-ai
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Run the Chess Bot

To run the chess bot, use the following command:
```bash
python bot.py
```

### Experiment with the Environment

Open the Jupyter Notebook to explore and customize the agent:
```bash
jupyter notebook environment.ipynb
```

---

## Technical Highlights

### Evaluation Function

- Utilizes **piece-square tables** for positional evaluation.
- Incorporates material and positional advantages in the scoring system.

### Move Ordering

- Implements **MVV-LVA** heuristic to prioritize captures and improve alpha-beta pruning efficiency.

### Quiescence Search

- Extends evaluations in high-tension positions to mitigate the "horizon effect."

### Iterative Deepening

- Provides dynamic depth control based on resource availability.

---

## Contributing

Contributions are welcome! Follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Special thanks to the **FIDE & Google Efficient Chess AI Challenge** organizers for the inspiration behind this project.

