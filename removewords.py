# remove some of the commonly occuring words
remove_words=['secret','needs','need','equivalent','candidate','hr','world','key','att','yr','yrs','year','years','competitive','salary','skill','skills','responsibilities','include','including','youve','helped','drive','action','actionable','questions','looking','help','understand','understands','understanding','role','such','etc','experience','in', 'on', 'to', 'www', 'it', 'is', 'we', 'us', 'com', 'was', 'your', 'have','has', 'see', 'what', 'how', 'very', 'with', 'most', 'his', 'her', 'own', 'who', 'able', 'use','passion','passionate','based','must', 'also', 'be', 'all', 'since', 'routinely', 'they', 'just', 'less', 'over', 'find', 'externally', 'rest', 'against', 'manager', 'through', '40', 'broader', 'weekly', 'digitally', 'skill', 'still', 'its', 'before', '25', 'now', 'bloomreach', 'rely', 'also', 'trigger', 'blindingly', 'behind', 'should', 'better', 'to', 'only', 'those', 'under', 'concisely', 'he', 'might', 'ca', '2012', 'persevere', 'then', 'them', 'fly', 'around', '1pm', 'very', 'intellectually', 'chantilly', 'background', 'differently', 'massively', 'fast', 'collaboratively', 'every', 'whether', 'closely', 'half', 'not', 'yourself', 'comply', 'timely', '60', 'internally', 'like', 'geographically', 'always', 'anytime', 'leader', 'these', 'eeo', 'assembly', 'she', 'each', 'further', 'identify', 'entirely', 'where', 'hacker', 'individually', 'attest', 'right', 'often', 'autonomously', 'bachelor', 'hard', 'some', 'discover', 'strategically', 'actively', 'culturally', 'professionally', 'unfairly', 'provider', 'incrementally', 'our', 'beyond', 'bigger', 'best', 'out', 'even', 'ultimately', 'throughout', 'for', 'away', 'currently', 'near', 'per', 'continually', 'consistently', 'outside', 'anywhere', 'above', 'between', 'seven', 'probably', 'three', 'youll', 'across', 'daily', 'core', 'we', 'never', 'recently', 'whose', 'initially', 'centrally', 'empower', 'million', 'deliver', 'however', 'here', 'quite', 'highly', 'explore', 'brightest', 'address', 'rapidly', 'along', 'fluently', 'by', 'both', 'about', '38', '3panel', 'ahead', 'of', 'could', 'dramatically', 'ingest', 'prior', 'plus', 'exponentially', 'conveniently', 'slightly', 'or', 'appropriately', 'equally', 'via', 'regardless', '1000s', 'previously', 'into', 'within', 'groupon', 'whatever', 'one', 'down', 'poly', 'because', 'long', 'another', 'apply', 'quickly', 'your', 'truly', 'readily', '100s', 'finally', 'analytically', 'from', 'would', 'monthly', 'nine', 'strictly', 'there', 'quicken', 'two', 'least', 'periodically', 'their', 'again', 'much', '15mm', 'typo', 'seriously', 'forward', 'legally', 'iteratively', 'really', 'more', 'tight', 'gummy', 'successfully', 'elsewhere', 'that', '1mm', 'shelf', 'excite', 'accurately', 'but', 'biggest', '2translating', 'withdrawn', 'specifically', 'personally', 'with', 'than', 'positively', 'must', 'toronto', '10', 'richest', 'this', 'proactively', 'originally', 'tremendously', 'up', 'us', 'worth', 'will', 'while', 'sour', 'tinder', 'can', 'were', 'continuously', 'locally', 'seamlessly', 'toward', 'solely', 'greater', 'regularly', 'concurrently', 'datadriven', 'viewer', 'it', 'proven', 'globally', 'effectively', 'as', 'at', 'in', 'ready', 'any', 'methodology', 'if', 'preferably', 'ideally', 'rather', 'self', 'when', 'thorough', 'clearly', '401k', 'post', 'potentially', 'which', 'largest', 'answer', 'you', 'incredibly', 'offshore', 'higher', 'visually', 'killer', 'http', 'deepest', 'though', 'may', 'after', 'upon', 'driven', 'most', '000', 'importantly', 'user', 'additionally', 'multiply', 'on', 'extremely', 'why', 'efficiently', 'billion', 'independently', 'off', 'especially', 'toptier', 'fully', 'maybe', 'gather', 'well', 'together', 'ia', 'directly', 'without', 'so', 'greatest', 'enterprise', '10s', 'five', 'infosphere', 'typically', 'latest','access']

remove_search_words=['field','use','love','results','result','based','applied','unique','deep','expert','experts','experience','experiences','extract','fun','ph','thriving','accessing','foundry','audience','pivotal','answering','need','perform','master-data','objects','golden','science-related','engineering-computer','science-computer','senior-software','learning-data','collective','new-data','working-large','approaches','simple','build','technologies','issues','processes','oriented-design','developing']
