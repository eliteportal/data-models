import frontmatter
import pandas as pd
from mdutils import fileutils

def test_reaction(pass): 
  if is.na(pass): 
    ":zzz:" # potentially skipped tests
  elif pass:
    ":white_check_mark:" 
  else:
    ":x:"

def md_link(url: str): 
  if len(url): 
    print(f"{template_link} ({url})")
  else: 
    print("")

## Template Generation
# The following manifest templates had at least one dependency with changes detected:


# ```{r parse-generation-logs, echo=FALSE}
# gen_logs = list.files("./logs", full.names = TRUE)
# templates = gsub("_log", "", basename(gen_logs))
# gen_test_results = lapply(gen_logs, readLines)
# gen_test_links = sapply(gen_test_results, md_link)
# gen_test_reaction = sapply(lengths(gen_test_results), test_reaction) 
# gen_report = data.frame(template = templates, 
#                          result = gen_test_reaction, 
#                          link = gen_test_links)
# knitr::kable(gen_report)
# ```

## :construction: Manifest Validation - COMING SOON

# # don't evaluate for now
# pass = "Your manifest has been validated successfully."
# config = jsonlite::read_json("validate/config.json")
# df = lapply(config.tests, `[`, c("manifest", "expect_pass", "expectation"))
# df = Reduce(rbind.data.frame, df)
# val_logs = list.files("validate/logs", full.names = TRUE)
# val_results = lapply(val_logs, readLines)
# val_pass = data.frame(
#   manifest = gsub(".txt", ".csv", basename(val_logs)),
#   pass = sapply(val_results, function(x) any(grepl(pass, x))))
# val_report = merge(df, val_pass, by = "manifest", all.x = TRUE)
# val_report$result = sapply(val_report.expect_pass == val_report.pass, test_reaction)

# # table to report: 
# val_report[, c("manifest", "result", "expectation")])


def create_template_page(term, term_dict):
    """load template for templates in data model"""
    post = frontmatter.load(Path(ROOT_DIR, "_layouts/template_page_template.md"))
    post.metadata["title"] = re.sub("([A-Z]+)|_", r" \1", term).strip()
    post.metadata["parent"] = term_dict["Module"]
    post.content = (
        "{% assign mydata=site.data."
        + re.sub("\s|/", "_", term)
        + " %} \n{: .note-title } \n"
        + f">{post.metadata['title']}\n"
        + ">\n"
        + f">{term_dict['Description']} [[Source]]({term_dict['Source']})\n"
        + post.content
    )

    # create file
    file = fileutils.MarkDownFile(
        str(Path(ROOT_DIR, f"docs/{term_dict['Module']}/{term}"))
    )

    # add content to the file
    file.append_end(frontmatter.dumps(post))

    return post
