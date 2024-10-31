import streamlit as st


def header():
    st.info(
        "I am currently running a survey to help Metaculus assess whether the tools on this site should be developed further and integrated into Metaculus. Please fill out this [Google Form](https://forms.gle/oM2NEaKrBbiAVNQS9) or give feedback in other ways (see bottom of page) if you don't have time for a survey. Please note that the tools are in beta, and there will be some inaccuracies."
    )


def footer():
    st.markdown("---")
    st.write(
        "For those willing to give feedback (even a quick thumbs up or down occasionally), please use the tools as much as you want (I'll give a message if costs become bad). Regular feedback is super valuable. Otherwise please donate to help support the project [☕️ Buy me a coffee](https://buymeacoffee.com/mokoresearch)"
    )
    st.write(
        "Please provide feedback by filling out this [Google Form](https://forms.gle/oM2NEaKrBbiAVNQS9). Give other feedback on [Discord](https://discord.gg/Dtq4JNdXnw) or email me at [moko.research@gmail.com](mailto:moko.research@gmail.com). Let me know what I can do to make this a tool you will want to use every day."
    )
    st.write(
        "Join the [Forecasting Meetup Discord](https://discord.gg/Dtq4JNdXnw) to practice forecasting with real people weekly."
    )
    st.write(
        "Queries made to the website are saved to a database and may be reviewed to help improve the tool"
    )
    st.write("Developed by [Ben Wilson](https://mokoresearch.com/).")
