import os

css_path = 'src/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replacements
replacements = {
    '.hero-text h1 {\n    font-family: \'Anton\', sans-serif;\n    font-size: clamp(2.8rem, 7vw, 5.5rem);\n    line-height: 1.1;\n    margin: 0 0 1.2rem;\n    letter-spacing: 2px;\n    text-transform: uppercase;\n    color: var(--text-white);': 
    '.hero-text h1 {\n    font-family: \'Anton\', sans-serif;\n    font-size: clamp(2.8rem, 7vw, 5.5rem);\n    line-height: 1.1;\n    margin: 0 0 1.2rem;\n    letter-spacing: 2px;\n    text-transform: uppercase;\n    color: var(--section-title-color, var(--text-white));',
    
    '.hero-text p {\n    font-size: clamp(1rem, 2.5vw, 1.25rem);\n    color: var(--text-muted);':
    '.hero-text p {\n    font-size: clamp(1rem, 2.5vw, 1.25rem);\n    color: var(--section-text-color, var(--text-muted));',
    
    '.cta-button {\n    display: inline-block;\n    text-decoration: none;\n    font-weight: 700;\n    font-size: 0.95rem;\n    letter-spacing: 1px;\n    text-transform: uppercase;\n    padding: 0.85rem 2.2rem;\n    border-radius: 8px;\n    cursor: pointer;\n    border: none;\n    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);\n    background: linear-gradient(135deg, var(--purple), var(--purple-light));\n    color: var(--gold);':
    '.cta-button {\n    display: inline-block;\n    text-decoration: none;\n    font-weight: 700;\n    font-size: 0.95rem;\n    letter-spacing: 1px;\n    text-transform: uppercase;\n    padding: 0.85rem 2.2rem;\n    border-radius: 8px;\n    cursor: pointer;\n    border: none;\n    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);\n    background: var(--section-btn-bg, linear-gradient(135deg, var(--purple), var(--purple-light)));\n    color: var(--section-btn-text, var(--gold));',

    '.cta-button-outline {\n    display: inline-block;\n    text-decoration: none;\n    font-weight: 700;\n    font-size: 0.95rem;\n    letter-spacing: 1px;\n    text-transform: uppercase;\n    padding: 0.85rem 2.2rem;\n    border-radius: 8px;\n    cursor: pointer;\n    background: transparent;\n    color: var(--gold);\n    border: 2px solid rgba(253, 204, 4, 0.5);':
    '.cta-button-outline {\n    display: inline-block;\n    text-decoration: none;\n    font-weight: 700;\n    font-size: 0.95rem;\n    letter-spacing: 1px;\n    text-transform: uppercase;\n    padding: 0.85rem 2.2rem;\n    border-radius: 8px;\n    cursor: pointer;\n    background: transparent;\n    color: var(--section-btn-bg, var(--gold));\n    border: 2px solid var(--section-btn-bg, rgba(253, 204, 4, 0.5));',

    'h2 {\n    font-family: \'Anton\', sans-serif;\n    font-size: clamp(2rem, 5vw, 3rem);\n    margin: 0 0 0.5rem;\n    color: #1f1d64;':
    'h2 {\n    font-family: \'Anton\', sans-serif;\n    font-size: clamp(2rem, 5vw, 3rem);\n    margin: 0 0 0.5rem;\n    color: var(--section-title-color, #ffffff);',

    '.section-subtitle {\n    color: var(--text-muted);':
    '.section-subtitle {\n    color: var(--section-text-color, var(--text-muted));',

    '.about-text p {\n    color: var(--text-muted);':
    '.about-text p {\n    color: var(--section-text-color, var(--text-muted));',

    '.course-title {\n    font-family: \'Anton\', sans-serif;\n    font-size: 1.15rem;\n    color: var(--text-white);':
    '.course-title {\n    font-family: \'Anton\', sans-serif;\n    font-size: 1.15rem;\n    color: var(--section-title-color, var(--text-white));',

    '.course-desc {\n    color: var(--text-muted);':
    '.course-desc {\n    color: var(--section-text-color, var(--text-muted));',
    
    '.contact-card-label {\n    font-size: 0.8rem;\n    letter-spacing: 2px;\n    text-transform: uppercase;\n    color: var(--text-muted);':
    '.contact-card-label {\n    font-size: 0.8rem;\n    letter-spacing: 2px;\n    text-transform: uppercase;\n    color: var(--section-text-color, var(--text-muted));',
    
    '.contact-card-value {\n    font-weight: 700;\n    font-size: 1rem;\n    color: var(--text-white);':
    '.contact-card-value {\n    font-weight: 700;\n    font-size: 1rem;\n    color: var(--section-title-color, var(--text-white));'
}

for old, new in replacements.items():
    if old in content:
        content = content.replace(old, new)
        print(f"Replaced: {old[:20]}...")
    else:
        print(f"FAILED: {old[:20]}...")

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Batch CSS replacement completed.")
