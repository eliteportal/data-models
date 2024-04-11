# ### --- Cleanup -------
# # Capitalize the column types
# dm["columnType"] = dm["columnType"].str.upper()

# # remove any duplicate values
# dm["columnType"] = (
#     dm["columnType"]
#     .fillna("")
#     .str.split(",")
#     .apply(lambda x: ",".join(np.unique(x)))
#     .replace("", np.nan)
# )
