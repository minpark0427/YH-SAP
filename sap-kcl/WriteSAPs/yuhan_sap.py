"""
Runner script for generating a Yuhan Corporation SAP from a protocol PDF.

Default backend is "claudecode" — calls the `claude` CLI using your subscription auth.
No API key needed. To use the Anthropic API instead, set ANTHROPIC_API_KEY and pass
--backend anthropic.

Usage:
    python -m WriteSAPs.yuhan_sap <protocol_pdf_path> [--test]
    python -m WriteSAPs.yuhan_sap <protocol_pdf_path> --backend anthropic
"""

import argparse
from pathlib import Path

from auto_sap.generate_templates.generate_yuhan_template import yuhan_template_v1


def main():
    parser = argparse.ArgumentParser(description="Generate a Yuhan SAP from a clinical trial protocol.")
    parser.add_argument("protocol", type=str, help="Path to the protocol PDF file.")
    parser.add_argument("--output-dir", type=str, default="SAPs", help="Directory to save the SAP output.")
    parser.add_argument("--test", action="store_true", help="Use a cheaper model (claude-haiku) for testing.")
    args = parser.parse_args()

    protocol_path = Path(args.protocol)
    if not protocol_path.exists():
        raise FileNotFoundError(f"Protocol not found: {protocol_path}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sap_name = f"YH_SAP_{protocol_path.stem}"

    yuhan_template_v1.write_sap(
        protocol_path=str(protocol_path),
        sap_name=sap_name,
        sap_folder_path=str(output_dir),
        test=args.test,
    )

    print(f"\nDone. Output in {output_dir}/")


if __name__ == "__main__":
    main()
