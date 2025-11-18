# Create __init__.py files for all modules
@"
"@ | Out-File -FilePath "src/__init__.py" -Encoding utf8

@"
"@ | Out-File -FilePath "src/web_ui/__init__.py" -Encoding utf8

@"
"@ | Out-File -FilePath "src/intent_engine/__init__.py" -Encoding utf8

@"
"@ | Out-File -FilePath "src/netconf_client/__init__.py" -Encoding utf8

@"
"@ | Out-File -FilePath "src/monitoring/__init__.py" -Encoding utf8

@"
"@ | Out-File -FilePath "src/failover/__init__.py" -Encoding utf8