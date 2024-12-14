#!/usr/bin/env python3
import yaml, argparse , sys, json, os, re, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
from parsel import Selector
from lib.parameters import process_parameters
from lib.request_body import process_request_body
from lib.responses import process_responses

def process_manifest(provider, debug):

    global error_codes_set

    """Process the API manifest file based on provider type."""
    # Determine which manifest file to read
    manifest_file = f"manifests/{provider}_api_manifest.yml"
    
    try:
        with open(manifest_file, 'r') as f:
            manifest = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {manifest_file} not found")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing {manifest_file}: {e}")
        sys.exit(1)

    # Process each service in the manifest
    for service_name, service_data in manifest['services'].items():
        for resource in service_data['resources']:
            resource_name = resource['name']
            for method in resource['methods']:
                process_endpoint(provider, service_name, resource_name, method['name'], method['docPath'], method['verb'], debug)

def scrape_dynamic_content(url):
    # Configure Selenium WebDriver with headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Specify the path to the downloaded ChromeDriver
    driver = webdriver.Chrome(
        service=Service("inc/chromedriver.exe"),
        options=chrome_options
    )

    try:
        # Open the page
        driver.get(url)

        # Wait for a specific element to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "root"))
        )

        # Extract the full rendered HTML
        page_source = driver.page_source

        # Parse the content using BeautifulSoup
        soup = bs4.BeautifulSoup(page_source, "html.parser")

        # Remove unwanted elements
        for tag in soup(["head", "script", "meta", "title", "style", "svg", "input", "iframe"]):
            tag.decompose()

        return soup

    finally:
        # Close the browser
        driver.quit()

def process_endpoint(provider, service, resource, method, docPath, sqlVerb, debug):
    global error_codes_set
    
    print(f"""processing docPath: {docPath}
provider: {provider}
service: {service}
resource: {resource}
method: {method}
sqlVerb: {sqlVerb}""")

    # Create output directory structure
    output_dir = f"staging/databricks_{provider}/{service}/{resource}"
    os.makedirs(output_dir, exist_ok=True)

    # Scrape the documentation page
    soup = scrape_dynamic_content(docPath)
    
    selector = Selector(text=str(soup))

    doc_base_path = "/html/body/div[1]/div/div[2]/div/div[2]/div[3]/article/div/div[1]"
    examples_doc_path = "/html/body/div[1]/div/div[2]/div/div[2]/div[3]/article/div/div[2]"

    http_verb = selector.xpath(f"{doc_base_path}/article/span/code/div/div/text()").get().lower()
    print(f"\nhttp_verb: {http_verb}") if debug else None
    if http_verb not in ["get", "post", "put", "delete", "patch"]:
        raise ValueError(f"Invalid HTTP verb: {http_verb}")

    http_path = selector.xpath(f"{doc_base_path}/article/span/code/span/text()").get()
    print(f"http_path: {http_path}") if debug else None
    if not http_path.startswith('/api/'):
        raise ValueError(f"Invalid HTTP path: {http_path}")
    
    op_desc = selector.xpath(f"{doc_base_path}/div[3]/div[2]/text()").get().replace("\n", " ").strip()
    print(f"op_desc: {op_desc}") if debug else None
    if op_desc is None:
        raise ValueError(f"Invalid operation description: {http_path}")

    params = process_parameters(selector, doc_base_path, debug)
    print(f"params: {params}") if debug else None

    request_body = process_request_body(selector, doc_base_path, examples_doc_path, False)
    print("request_body:", json.dumps(request_body, indent=2)) if debug else None

    responses = process_responses(selector, doc_base_path, debug)
    print("responses:", json.dumps(responses, indent=2)) if debug else None

    # stitch complete operation object together
    operation = {
        http_path: {
            http_verb: {
                "description": op_desc,
                "operationId": f"{resource}-{method}".replace("_", "-"),
                "externalDocs": {"url": docPath},
                "x-stackQL-resource": resource,
                "x-stackQL-method": method,
                "x-stackQL-verb": sqlVerb,
                "x-numReqParams": len([param for param in params if param.get("required")]),
                "parameters": params,
                "requestBody": request_body,
                "responses": responses,
            }
        }
    }

    write_output(output_dir, method, operation)

    print(f"\n========\n")


def write_output(output_dir, method, result):
    print(f"\nWriting output to {output_dir}/{method}.json\n")
    # Write the output with prettified JSON format
    output_file = f"{output_dir}/{method}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=1)

def clean_target_dir(provider):
    """Clean the target directory and all subdirectories"""
    target_dir = f"staging/databricks_{provider}"
    if os.path.exists(target_dir):
        print(f"Cleaning directory: {target_dir}\n")
        print(f"========\n")
        for root, dirs, files in os.walk(target_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(target_dir)

error_codes_set = set()

def main():
    global error_codes_set

    start_time = time.time()

    parser = argparse.ArgumentParser(description='Process Databricks API documentation')
    parser.add_argument('provider', choices=['account', 'workspace'],
                      help='The provider type to process (account or workspace)')
    parser.add_argument('--debug', action='store_true',
                      help='Save raw text files alongside JSON for debugging')

    args = parser.parse_args()
    
    # Clean target directory before processing
    clean_target_dir(args.provider)

    # Process the manifest for the specified provider
    process_manifest(args.provider, args.debug)    

    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

    # At the end of main()
    with open('error_codes.txt', 'r') as f:
        unique_codes = sorted(set(f.read().splitlines()))
    print(f"All error codes found: {unique_codes}")

if __name__ == "__main__":
    main()