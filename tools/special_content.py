"""Structured content for the hand-designed company pages.

All copy is Rhoden Roofing's own wording, taken from the live site (including the text inside
the "Proven Process" infographics). Images are paths under wp-content/uploads and are mapped to
local assets by build.py.
"""

VALUES_CULTURE = [  # wording from /about/culture/ and /about/sell-your-business/
    {"name": "Evolve and Adapt", "icon": "2024/12/Sprouting-Leaf-Interface-Icon-Downsized-Blue.png",
     "text": "We continually acquire knowledge to enhance our capabilities. Both personally and professionally, there is room for self-improvement. Instead of seeing mistakes as failures, we perceive them as valuable learning opportunities that enable us to rectify any issues and provide exceptional customer service."},
    {"name": "Be a Great Teammate", "icon": "2024/12/Teammate-Interface-Icon-2-Blue-256x.png",
     "text": "Respect, sincerity and high expectations guide our interactions. We foster open, honest communications, embracing tough conversations and feedback to address blind spots. We lift up struggling teammates. When there is adversity we seek solutions, not excuses, which promotes team success and sustainable culture."},
    {"name": "Get It Done", "icon": "2024/12/Get-It-Done-Interface-Icon-Gear-Blue.png",
     "text": "We are 100% accountable to our customers and teammates. Customers trust us to build exceptional roofing systems. We take that commitment seriously. We will do whatever is necessary to overcome obstacles & find solutions to deliver extraordinary results."},
    {"name": "Do the Right Thing", "icon": "2024/12/Compass-Interface-Icon-Blue-and-Red.png",
     "text": "What do you do when no one else is looking? Always put yourself in the shoes of your customer when faced with a decision, treating their property as if it were your own. Act with integrity and honesty, always choosing what’s right over what’s easy."},
]

VALUES_CAREERS = [  # wording from /careers/
    dict(VALUES_CULTURE[0], text="If you are not constantly learning and improving, you are not reaching your full potential. Everyone in the company can always be improving themselves inside and outside the company. A mistake or a “loss” should only be viewed as an opportunity to learn and grow to make yourself and the company better in the future."),
    VALUES_CULTURE[1], VALUES_CULTURE[2], VALUES_CULTURE[3],
]

BRAND_WORDS = ["Dedicated", "Honest", "Humble", "Quality"]  # from the Proven Process infographic

APART = [  # "What sets us apart", /careers/
    {"name": "Beat the Budget", "slug": "beat-the-budget",
     "paras": ["Our Beat the Budget bonus structure is a revenue-sharing program that ensures outstanding performance benefits everyone. While the end of a quarter might be business as usual elsewhere, at Rhoden Roofing, it’s an opportunity to celebrate company-wide achievement and reward the hard work that made it possible."]},
    {"name": "EOS", "slug": "eos",
     "paras": ["Too often, meetings feel like a formality: scheduled, attended, and quickly forgotten. At Rhoden Roofing, we’ve embraced the Entrepreneurial Operating System (EOS) to ensure every meeting serves a purpose.",
               "Using EOS’ L10 framework, we set clear quarterly goals, or “rocks,” and track progress in weekly meetings. If a meeting misses the mark, participants rate it, and we adjust to stay on course. This approach ensures every voice is heard, every issue is addressed, and everyone knows what they’re working toward."]},
    {"name": "Complete Ownership", "slug": "ownership",
     "paras": ["Hanging a photo in a rental property means worrying about patching the wall before your lease is up. Hanging a photo in a home you own is different: your only concern is making it fit, making it yours.",
               "At Rhoden Roofing, we believe your work should belong to you. Everyone on our team takes pride in owning their work and ensuring it’s completed with care."]},
    {"name": "State of the Company", "slug": "state-of-the-company",
     "paras": ["Imagine trying to solve a problem you didn’t know existed; it’s impossible. The same is true for a company. That’s why at Rhoden Roofing, we share everything: our challenges, successes, and plans for the future. Every quarter you review your supervisor in one-on-ones designed to find your paths to career growth with Rhoden Roofing.",
               "Our State of the Company meetings ensure everyone knows where we stand and where we’re headed. No backroom discussions, no trickle-down updates: just facts, shared openly with the entire team."]},
    {"name": "Comprehensive Benefits", "slug": "benefits",
     "paras": ["When your foundation is secure, you can focus on building your future. At Rhoden Roofing, we provide the stability you need to thrive."]},
]
BENEFITS = [
    ("Health", "Comprehensive health insurance, including vision and dental"),
    ("401(k)", "A 401(k) plan with company matching to help you invest in what matters most"),
    ("Paid time off", "Immediate access to Paid Time Off upon hire"),
    ("Bonuses", "Bonuses that reward your contributions"),
]

TEAMS = [  # /careers/ "Our Teams"
    {"name": "Project Coordination", "img": "2025/01/Roofing-Professional-Answering-Customer-Questions.webp", "alt": "Project Coordinator and customer reviewing a roof plan at a table",
     "text": "Project Coordinators are the customer’s trusted partner. They design custom roof systems, address challenges proactively, and bring their vision to life. It’s about relationships, expertise, and delivering excellence.",
     "tag": "The expert customers remember and the partner that earned their trust."},
    {"name": "Marketing", "img": "2025/01/Behind-the-Scenes-of-a-Rhoden-Roofing-Commercial.webp", "alt": "Behind the scenes of a Rhoden Roofing commercial shoot",
     "text": "Marketing’s job is to connect people to Rhoden Roofing: sharing our story, showcasing our work, and ensuring we’re not strangers when we meet. It’s about crafting messages that inspire, inform, and echo the excitement we have.",
     "tag": "We make sure they know us before they meet us."},
    {"name": "Claims", "img": "2025/01/Chalking-a-Roof-for-Insurance-Claim.webp", "alt": "Roofing professional chalking hail hits on a roof for an insurance claim",
     "text": "Our Claims team is the bridge between customers and their insurers, simplifying the process and securing what customers are owed. They’re expert guides in a system that often feels overwhelming.",
     "tag": "Advocates for every claim, partners at every step."},
    {"name": "Production", "img": "2025/01/Production-Foreman.webp", "alt": "Production foreman carrying roofing material on a roof",
     "text": "Roof replacements and repairs can be construction projects with many moving parts. Our production team brings it all together by efficiently managing time, resources, and communication with precision.",
     "tag": "Fulfilling our promise of a roof that lasts a lifetime."},
    {"name": "Operations", "img": "2025/01/pexels-fauxels-3184292.webp", "alt": "Operations team members reviewing work together",
     "text": "Operations works behind the scenes to ensure everything runs smoothly, identifying inefficiencies both internally and externally. They provide seamless support, enabling teams to focus on delivering exceptional results.",
     "tag": "Turning small actions into big impacts."},
]

HIRING = [  # /careers/ "How We Hire", in order
    ("Explore our roles", "Our hiring process starts with a genuine desire to be a part of something bigger."),
    ("Hear back", "We personally respond to every question. The best way for us to learn how you might align with our values is to learn about you."),
    ("Evaluation", "Hiring is a two-way street: while we evaluate your fit for the role, you’re evaluating us. Bring questions that help you explore what it’s like to be a part of our team."),
    ("The interview", "Some positions comprise a round-robin interview with the relevant department, while leadership or specialized roles comprise multiple interviews with team members and leaders to provide deeper insight into our culture and expectations."),
    ("The timeline", "Depending on the position, the hiring timeline can vary from a few days to a few weeks. Seasonal factors may also affect the start date, especially for project coordinator roles."),
    ("The opportunity", "Growth is part of our DNA, and we will align talent with opportunity."),
    ("Meet the team", "During your first two weeks, you’ll meet with every department and leadership team member, including the owner and COO. You’re encouraged to ask questions and receive honest answers from everyone on the team."),
    ("Set up for success", "From day one, we provide the tools, training, and support needed for success. We don’t believe in “sink or swim”; we believe in setting you up to thrive."),
    ("Contribute", "The perfect background doesn’t matter to us. It’s more important that you’re genuine and ready to contribute. We’re committed to finding the right seat for the right person."),
]

PROCESS = [  # transcribed from the "Proven Process" infographic
    {"name": "Needs Analysis", "items": ["Initial on-site meeting", "Gather all measurements", "Complete photo checklist", "Spotlight on your needs", "Understand your goals"]},
    {"name": "Design & Presentation", "items": ["Estimator builds quote", "Roof designed to city code and manufacturer specs", "Demonstration of “roofing system”", "What to expect", "Address your questions or concerns", "Discuss timeline"]},
    {"name": "Behind the Scenes", "items": ["Address any insurance supplements", "Confirm design is to spec", "Schedule your job", "Order materials"]},
    {"name": "Production of Roof", "items": ["Project manager introduction", "On-site pre-construction meeting", "Confirm scope of work", "Ensure roof built to city code and manufacturer specs", "Photo documentation", "Ensure 100% customer satisfaction"]},
    {"name": "Finalization of Process", "items": ["Create photo report for insurance", "Assist you with insurance paperwork", "Finalize any supplements and send invoice", "Obtain your feedback"]},
]
PROCESS_REVIEWS = [  # from the infographic
    {"name": "Heidi L.", "role": "Customer", "text": "I was a little hesitant when I found out we had to get our roof redone. You always hear about the horror stories that come with replacing your roof with insurance and the quality of work being performed. Erica was our contact with Rhoden and she was absolutely awesome! Rhoden Roofing always answered all my questions and our experience couldn’t have been any smoother. All of the team members walked us through every part of the process and made sure to communicate all extra costs we would endure due to upgrades we wanted. Our roof & gutters look amazing!"},
    {"name": "Jason E.", "role": "Property Manager", "text": "Hands down the best roofing company I have ever dealt with! With a multi-building property and a couple hundred residents, it is critical to have a professional group on hand to navigate the many obstacles that come with replacing roofs. Rhoden sets the bar! Communication was second to none as they formulated a course of action allowing us to properly notify our tenants and eliminate the typical complaints often received with this scale of work."},
    {"name": "Barbara W.", "role": "Customer", "text": "In a nutshell my experience with Rhoden Roofing has been that we received honest, prompt and courteous service. I requested Rhoden Roofing to check a leak in our attached garage. Within two days of my call a representative was at our home. After a thorough check of the roof they determined that the true problem was not the roof itself, but involved a window unit and its “metal roof pan” located in the roof under the window. Within three days the repairs were made and there has been no leaking since."},
]

WARRANTY = {
    "promise": ["Replacing your roof is one of the most important choices, and likely the biggest investment, that you will make as a homeowner.",
                "Most Wichita roofing contractors have a 1–5 year warranty on their workmanship. At Rhoden Roofing, we offer Wichita’s only Double-Lifetime Workmanship Warranty. We guarantee our workmanship for any defect in installation for the LIFETIME of the roof."],
    "pillars": [("Install the Best Products", "product"), ("Employ the Best People", "people"), ("Developed the Best Process", "process")],
    "steps": [("Document any damage", "We’ll document any damage we see when we get there, but documenting damage early can help us identify the problem."),
              ("Call us", "We take our promise to customers seriously before, during, and after installation. Call us at (316) 927-2233 and let us take care of it for you.")],
}

CERTS = [  # /manufacturer-certifications/
    {"group": "Steep slope", "note": "Pitched roofs: shingles, tile, slate and synthetics", "items": [
        ("GAF Master Elite Contractor", "2020/12/MASTER_ELITE-300x110-1.png"),
        ("MasterPiece Contractor, DaVinci Roofscapes", "2020/12/davinci-masterpiece-contractor-300x215-1.png"),
        ("Crown Roofer, Ludowici", "2020/12/crown-roofer.png"),
        ("Malarkey Emerald Premium Contractor", "2020/12/malarkey-certified-residential-contractor-denver.jpg"),
        ("IKO ShieldPRO Plus Contractor", "2020/12/iko-shield-pro-plus-contractor.jpg")]},
    {"group": "Low slope", "note": "Flat and low-slope commercial membrane systems", "items": [
        ("GAF Master Elite (commercial)", "2020/12/854.jpg"),
        ("Gen Flex Roofing Systems", "2020/12/855.jpg"),
        ("Mule-Hide Products", "2020/12/503.jpg")]},
    {"group": "Inspection & estimating", "note": "Ventilation, claims estimating and roof inspection", "items": [
        ("Air Vent Inc.", "2020/12/571.jpg"),
        ("Xactimate Certified", "2020/12/xactimate-logo.jpg"),
        ("HAAG Certified Inspector, commercial roofs", "2020/12/haag-certified-inspector-commercial-roofs-1-1.jpg"),
        ("HAAG Certified Inspector, residential roofs", "2020/12/haag-certified-inspector-residential-roofs-1.jpg")]},
]

AWARDS = {  # /awards/ plus the homepage's 2025 award
    "feature": {"name": "Wichita's 2025 Small Business of the Year", "by": "Wichita Regional Chamber of Commerce",
                "img": "2025/09/Rhoden-Roofing-LLC-SBA-Winner-Transparent-PNG.png",
                "url": "https://www.wichitachamber.org/blog/2025/07/16/small-business-awards/chamber-celebrates-2025-small-businesses-of-the-year/"},
    "series": [
        {"name": "The Wichita Eagle Readers’ Choice", "years": [
            ("2012", "2020/12/winner-2012.jpg"), ("2013", "2020/12/winner-2013.jpg"), ("2014", "2020/12/winner-2014.jpg"), ("2015", "2020/12/winner-2015.jpg"),
            ("2016", "2020/12/winner-2016.jpg"), ("2017", "2020/12/winner-2017.jpg"), ("2018", "2020/12/readers-choice-2018ee.jpg"), ("2019", "2020/12/readers-choice-2019ee.jpg")]},
        {"name": "Angie’s List Super Service Award", "years": [
            ("2011", "2020/12/Angies-list-2011-Super-Service-Award.jpg"), ("2012", "2020/12/Angies-list-2012-Super-Service-Award.jpg"), ("2013", "2020/12/Angies-list-2013-Super-Service-Award.jpg"),
            ("2014", "2020/12/Angies-list-2014-Super-Service-Award.jpg"), ("2015", "2020/12/Angies-list-2015-Super-Service-Award.jpg"), ("2016", "2020/12/Angies-list-2016-Super-Service-Award.jpg"),
            ("2017", "2020/12/Angies-list-2017-Super-Service-Award.jpg")]},
    ],
    "agc": {"name": "Association of General Contractors Award of Excellence", "img": "2020/12/IMG_0168-e1528994276707.jpg"},
}

SELL = {
    "intro": ["While Rhoden Roofing exists to protect what matters most, our purpose is to delight our customers, serve our teammates, and give back to the community."],
    "growth": "Rhoden Roofing is interested in growing our team by adding residential roofing locations in cities within a 500-mile radius of Wichita, KS. We currently serve residential customers in the Wichita area, and serve commercial and multifamily roofing clients across a 4-state region: Kansas, Missouri, Oklahoma, Arkansas.",
    "fit": "We are looking to buy roofing locations with existing teams who align with our core values. We represent quality roofing and long-term relationships with our customers via lifetime and double-lifetime workmanship warranties. Therefore, good people and quality roofing are the two most important factors for a viable acquisition fit.",
    "options": "If you are looking to get out of the roofing business, or get relief from the financial worry of running a business day-to-day, consider joining the stability of Rhoden Roofing. We are open to both a departing sale, or a transition period where the departing owner stays on as location manager.",
    "states": ["Kansas", "Missouri", "Oklahoma", "Arkansas"],
}

AUTHOR = {  # shown in the author box on every Learning Center article
    "name": "Rhoden Roofing",
    "title": "Wichita roofing contractor since 2008",
    "bio": "Rhoden Roofing was founded in Wichita by John Rhoden in 2008 and installs, repairs and replaces "
           "residential and commercial roofs across Wichita and south-central Kansas. Our Learning Center articles "
           "explain what our project coordinators, inspectors and crews see on Kansas roofs, so you can make an "
           "informed decision about yours.",
    "creds": ["GAF President’s Club", "GAF Master Elite", "HAAG Certified Inspectors", "2025 Wichita Small Business of the Year"],
}
AUTHORS_BY_WP_ID = {}  # e.g. {9: {"name": "...", "title": "...", "bio": "...", "photo": "2024/..."}} to credit a named expert
