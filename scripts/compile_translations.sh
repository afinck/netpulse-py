#!/bin/bash

# Compile translation files for Netpulse

echo "Compiling translations..."

# Compile German translations
echo "Compiling German translations..."
cd netpulse/translations
pybabel compile -d de/LC_MESSAGES -i de/LC_MESSAGES/messages.po --directory=.
if [ $? -eq 0 ]; then
    echo "✅ German translations compiled successfully"
else
    echo "❌ Failed to compile German translations"
    exit 1
fi

# Compile English translations
echo "Compiling English translations..."
pybabel compile -d en/LC_MESSAGES -i en/LC_MESSAGES/messages.po --directory=.
if [ $? -eq 0 ]; then
    echo "✅ English translations compiled successfully"
else
    echo "❌ Failed to compile English translations"
    exit 1
fi

echo "🎉 All translations compiled successfully!"
echo "Available languages: de, en"
