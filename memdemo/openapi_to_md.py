# openapi_to_md.py
import json
import sys
from pathlib import Path

def openapi_to_markdown(spec):
    md = []
    md.append("# API Documentation\n")
    md.append(f"**Title**: {spec.get('info', {}).get('title', 'N/A')}\n")
    md.append(f"**Version**: {spec.get('info', {}).get('version', 'N/A')}\n")
    
    paths = spec.get("paths", {})
    for path, methods in paths.items():
        for method, details in methods.items():
            md.append(f"## {method.upper()} `{path}`\n")
            
            summary = details.get("summary", "")
            if summary:
                md.append(f"{summary}\n")
            
            # Request Body
            if "requestBody" in details:
                content = details["requestBody"].get("content", {})
                if "application/json" in content:
                    schema = content["application/json"]["schema"]
                    md.append("### Request Body (JSON)\n")
                    md.append("```json\n")
                    md.append(json.dumps(schema.get("example", {}), indent=2, ensure_ascii=False))
                    md.append("\n```\n")
                    
                    # Try to extract properties
                    if " $ ref" in schema:
                        ref_name = schema[" $ ref"].split("/")[-1]
                        components = spec.get("components", {}).get("schemas", {})
                        if ref_name in components:
                            props = components[ref_name].get("properties", {})
                            if props:
                                md.append("| Field | Type | Required | Description |\n")
                                md.append("|-------|------|----------|-------------|\n")
                                required_list = components[ref_name].get("required", [])
                                for field, info in props.items():
                                    req = "Yes" if field in required_list else "No"
                                    desc = info.get("description", "")
                                    ftype = info.get("type", "object")
                                    md.append(f"| `{field}` | `{ftype}` | {req} | {desc} |\n")
                                md.append("\n")
            
            # Responses
            responses = details.get("responses", {})
            if responses:
                md.append("### Responses\n")
                for code, resp in responses.items():
                    desc = resp.get("description", "")
                    md.append(f"- **{code}** {desc}\n")
                    if "application/json" in resp.get("content", {}):
                        example = resp["content"]["application/json"].get("example")
                        if example:
                            md.append("  ```json\n")
                            md.append("  " + json.dumps(example, indent=2, ensure_ascii=False).replace("\n", "\n  "))
                            md.append("\n  ```\n")
                md.append("\n")
    return "\n".join(md)

def main():
    if len(sys.argv) != 3:
        print("Usage: python openapi_to_md.py <openapi.json> <output.md>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    with open(input_file, "r", encoding="utf-8") as f:
        spec = json.load(f)
    
    markdown = openapi_to_markdown(spec)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    print(f"✅ Markdown 文档已生成: {output_file}")

if __name__ == "__main__":
    main()