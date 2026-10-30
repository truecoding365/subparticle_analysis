#!/usr/bin/env python3
import argparse
import os
from collections import Counter
import matplotlib.pyplot as plt

def parse_star_file(star_file, target_column="_rlnImageOriginalName"):
    """
    Parse a RELION-style STAR file and extract target column values.
    """
    with open(star_file, 'r') as f:
        lines = f.readlines()

    header_indices = {}
    data_started = False
    data = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Detect header definitions
        if line.startswith('_rln'):
            parts = line.split()
            if len(parts) >= 2 and parts[-1].startswith('#'):
                col_name = parts[0]
                col_index = int(parts[-1].replace('#', '')) - 1
                header_indices[col_name] = col_index
            continue

        # Data lines
        if header_indices and not line.startswith('_rln'):
            data_started = True

        if data_started:
            data.append(line.split())

    if target_column not in header_indices:
        raise ValueError(f"Column '{target_column}' not found in the STAR file.")

    target_idx = header_indices[target_column]
    values = [row[target_idx] for row in data if len(row) > target_idx]

    return values


def calculate_quartiles(values):
    """
    Calculate the first (Q1) and third (Q3) quartiles for a list of values.
    """
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 0:
        return 0.0, 0.0

    def median(lst):
        mid = len(lst) // 2
        if len(lst) % 2 == 0:
            return (lst[mid - 1] + lst[mid]) / 2.0
        else:
            return lst[mid]

    if n % 2 == 0:
        lower = sorted_vals[:n // 2]
        upper = sorted_vals[n // 2:]
    else:
        lower = sorted_vals[:n // 2]
        upper = sorted_vals[n // 2 + 1:]

    q1 = median(lower)
    q3 = median(upper)
    return q1, q3


def plot_histogram(star_file, target_column="_rlnImageOriginalName", output=None):
    """
    Plot a frequency histogram of elements in the target column, 
    displaying the mean, Q1–Q3 range, and full range in the legend, and export the data.
    """
    plt.figure(figsize=(8, 4))

    values = parse_star_file(star_file, target_column=target_column)
    counts = Counter(values)
    freq_values = list(counts.values())

    if not freq_values:
        print(f"⚠️ No entries found for column {target_column}")
        return

    # Calculate statistics
    mean_val = sum(freq_values) / len(freq_values)
    q1_val, q3_val = calculate_quartiles(freq_values)
    min_val = min(freq_values)
    max_val = max(freq_values)
    
    # Format legend text to include Mean, Q1–Q3, and Full Range
    legend_text = (
        f"Mean: {mean_val:.2f}\n"
        f"Q1–Q3: {q1_val:.1f} – {q3_val:.1f}\n"
        f"Range: {min_val} – {max_val}"
    )
    
    x_bins = range(0, max_val+2)
    #x_bins = range(0,60)
    bin_edges = [x - 0.5 for x in range(0, max_val + 2)]


    #hist_vals, bin_edges, _ = plt.hist(
    hist_vals, _, _ = plt.hist(
        freq_values,
        #bins=x_bins,
        bins=bin_edges,
        alpha=0.7,
        linewidth=0.5,
        color='red',
        edgecolor="black",
        label=legend_text,
#        align='right'
    )

    #plt.xlabel(f"Frequency of {target_column}")
    plt.xlabel("Frequency of L2 densities", fontsize='x-large')
    plt.ylabel("Counts",fontsize='x-large')
    plt.legend(loc='best', fontsize='x-large', frameon=True)
    plt.xticks(fontsize='large')
    plt.yticks(fontsize='large')
    plt.tight_layout()

    # Determine output base name
    if output:
        base_name, _ = os.path.splitext(output)
        txt_file = f"{base_name}_histogram.txt"
        img_file = f"{base_name}_histogram.png"
    else:
        txt_file = "histogram_data.txt"
        img_file = None

    # Write integer x-values + counts
    with open(txt_file, "w") as f:
        f.write("#x_value\tcount\n")
        for x, count in enumerate(hist_vals):
            f.write(f"{x}\t{int(count)}\n")

    print(f"Histogram data saved to {txt_file}")

    # Save or show image
    if img_file:
        plt.savefig(img_file, dpi=300)
        print(f"Histogram image saved to {img_file}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot frequency histograms of elements in a STAR file column with mean, Q1-Q3, and range in legend."
    )
    parser.add_argument("input_star", help="Input STAR file (e.g. particles.star)")
    parser.add_argument("--column", default="_rlnImageOriginalName",
                        help="Column name to analyze (default: _rlnImageOriginalName)")
    parser.add_argument("-o", "--output", help="Prefix or filename for output files (e.g. procapsid_VP3)")
    args = parser.parse_args()

    plot_histogram(args.input_star, target_column=args.column, output=args.output)


if __name__ == "__main__":
    main()