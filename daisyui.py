import scrapy
import re
import os


class DaisyuiSpider(scrapy.Spider):
    name = "daisyui"
    allowed_domains = ["daisyui.com"]
    start_urls = ["https://daisyui.com/components/button/"]

    # Create docs directory in the spider's init
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.docs_dir = os.path.join(os.getcwd(), "docs")
        os.makedirs(self.docs_dir, exist_ok=True)

    def parse(self, response):
        # Extract the component name from the URL
        component_name = response.url.rstrip("/").split("/")[-1]
        component_name = re.sub(r"[^\w\-]", "_",
                                component_name)  # Sanitize filename

        # Prepare file path
        file_path = os.path.join(self.docs_dir, f"{component_name}.txt")

        # Collect all content for this page
        content = []
        for section in response.css(".component-preview"):
            title = section.css("div span::text").get() or ""
            inner_html = section.css(".preview").get()
            if inner_html:
                inner_html = inner_html[inner_html.find(">") +
                                        1:inner_html.rfind("<")]
                # Remove HTML comments
                inner_html = re.sub("<!--.*?-->",
                                    "",
                                    inner_html,
                                    flags=re.DOTALL)
            content.append(f"title: {title}\nexample: {inner_html}\n---\n")

        # Write all content to the file once
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(content)

        # Follow links to other components
        for link in response.css("a[href*=components]"):
            url = link.xpath("@href").get()
            if url and url.startswith("/components"):
                yield response.follow(url, callback=self.parse)
