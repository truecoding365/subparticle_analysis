#!/usr/bin/env python3
import argparse

def read_star_field_values(star_file, field_name):
    """
    Reads a STAR file and extracts all values under the given field name.
    Returns a set of those values.
    """
    values = set()
    with open(star_file, 'r') as f:
        lines = f.readlines()

    # Find the field index
    field_index = None
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped.startswith(field_name):
            parts = line_stripped.split()
            if len(parts) >= 2 and parts[1].startswith("#"):
                field_index = int(parts[1][1:]) - 1
            break

    if field_index is None:
        raise ValueError(f"Field {field_name} not found in {star_file}")

    # Extract values from data rows
    for line in lines:
        line_stripped = line.strip()
        if (not line_stripped or line_stripped.startswith("#") or line_stripped.startswith("_") or line_stripped.startswith("data_") or line_stripped.startswith("loop_")):
            continue

        parts = line_stripped.split()
        if len(parts) > field_index:
            values.add(parts[field_index])

    return values


def match_lines(file2, field_name_2, match_values):
    """
    Returns lines from file2 where the given field contains a value in match_values.
    """
    with open(file2, 'r') as f:
        lines = f.readlines()

    # Find field index in file2
    field_index = None
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith(field_name_2):
            parts = line_stripped.split()
            if len(parts) >= 2 and parts[1].startswith("#"):
                field_index = int(parts[1][1:]) - 1
            break


    if field_index is None:
        raise ValueError(f"Field {field_name_2} not found in {file2}")

    header = []
    matched_lines = []

    for line in lines:
        line_stripped = line.strip()
        if (not line_stripped or 
            line_stripped.startswith("#") or 
            line_stripped.startswith("_") or 
            line_stripped.startswith("data_") or 
            line_stripped.startswith("loop_")):
            header.append(line)
        else:
            parts = line_stripped.split()
            if len(parts) > field_index and parts[field_index] in match_values:
                matched_lines.append(line)

    return header, matched_lines


def main():
    parser = argparse.ArgumentParser(description="Match _rlnImageName from file1 with _rlnImageOriginalName from file2.")
    parser.add_argument("file1", help="First STAR file (source of _rlnImageName)")
    parser.add_argument("file2", help="Second STAR file (where lines will be selected)")
    parser.add_argument("--field", default="_rlnImageName", help="Field name to match (default: _rlnImageName)")
    parser.add_argument("output", help="Output STAR file")
    args = parser.parse_args()

    # Extract all _rlnImageName values from file1
    print(f"Reading values from {args.file1} using field {args.field}...")
    names = read_star_field_values(args.file1, args.field)
    print(f"Found {len(names)} unique values in {args.file1}.")

    # Extract matching lines from file2
    print(f"Filtering lines from {args.file2}...")
    header, matches = match_lines(args.file2, args.field, names)

    # Save output
    with open(args.output, "w") as out:
        out.writelines(header)
        out.writelines(matches)

    print(f"Saved {len(matches)} matched lines to: {args.output}")


if __name__ == "__main__":
    main()

