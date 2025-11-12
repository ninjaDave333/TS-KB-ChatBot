# before making any change to the code, make sure to address the relevant docs in docs\ including ADR.md
# everytime a an important design desicion is made, or a problem solved, make sure to document it in all relevant docs in docs\ and docs\ADR.md
# everytime a new feature is fully tested and confirmed working, update docs\CHANGELOG.md
# if you try to use a new MS Graph API, consult with your ms graph mcp.
# if you try to generate terraform code, consult with your terraform mcp first.
# if you try to generate any type of code or api, try to fetch latest relevant docs using your terraform context7 mcp.
# get explicit user approval if you think about changing any schema in the project.
# when trying to exectute code make sure you are enabling the venv first.
# if adding any new packages to the project make sure to add them to Requirements.txt, and prompt the user to install them. also make sure it is updated in relevant docs.
# if you generate any test or temporary scripts, try to contain them in the Tests folder only for a cleaner environment.
# the SchemaSync.md file in the /docs folder contains the full schema and relation details created by this tool, and should be always up-to-date, it will be used to sync with other service projects that consume this data, be detailed and write it in an LLM ready and optimized format.