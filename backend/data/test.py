from langchain_community.document_loaders import CSVLoader
loader = CSVLoader("通识选课2.csv", encoding='utf-8')
documents = loader.load()
print(documents[:100])