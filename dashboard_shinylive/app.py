from pathlib import Path
import joblib, pandas as pd
import sklearn
from shiny import App, reactive, render, ui

ROOT = Path(__file__).resolve().parent
WWW, FIGS = ROOT / "www", ROOT / "figures"
df = pd.read_csv(ROOT / "cross_border_ecommerce_supply_chain_dataset.csv")
pkg = joblib.load(ROOT / "delivery_delay_logistic_model.joblib")
pre, mdl = pkg["preprocessor"], pkg["model"]

if not hasattr(mdl, "multi_class"):
    mdl.multi_class = "auto"
thr, fcols = float(pkg["decision_threshold"]), pkg["original_feature_columns"]
pidx = list(mdl.classes_).index(pkg["positive_class_value"])
CHOICES = {str(i): f"{df.loc[i,'Order_ID']} | {df.loc[i,'Region']} | {df.loc[i,'Shipping_Mode']}" for i in range(25)}

CSS = """
body{background:#f6f3fb;font-family:'Segoe UI',sans-serif;color:#2d2638}.container-fluid{max-width:1500px!important}
.navbar{background:#4b286d!important;border-bottom:3px solid #b78bd4}.navbar-brand,.navbar-nav .nav-link{color:#fff!important}.navbar-brand{font-weight:700}
.tab-content{padding:20px 24px}.hero{background:linear-gradient(135deg,#4b286d,#8a5aa8);color:#fff;border-radius:12px;padding:22px 28px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center}
.hero h1{font-size:24px;font-weight:700;margin:0}.hero p{color:#eadcf2;margin:2px 0 0}.live{background:#ffffff22;border:1px solid #ffffff55;padding:5px 12px;border-radius:16px;font-size:11px}
.krow{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px}.kpi{background:#fff;border:1px solid #eadff0;border-top:4px solid #8a5aa8;border-radius:10px;padding:14px 16px}
.kpi.r{border-top-color:#b64b4b}.kpi.g{border-top-color:#4c8b72}.kpi.a{border-top-color:#d08a33}.kl{font-size:10px;font-weight:700;letter-spacing:.05em;color:#766c80;text-transform:uppercase}
.kv{font-size:22px;font-weight:700}.ks,.st{font-size:11px;color:#766c80}.card{border:1px solid #eadff0!important;border-radius:10px!important;margin-bottom:18px}.card-header{background:#f8f5fb!important;color:#4b286d;font-weight:600}
.btn-primary{background:#8a5aa8!important;border-color:#8a5aa8!important;width:100%;padding:10px;font-weight:600}.ac{border-top:4px solid #d08a33!important;min-height:500px}.pw{text-align:center;padding:14px 6px}
.pl{font-size:11px;color:#766c80;text-transform:uppercase}.pn{font-size:52px;font-weight:700}.rp{display:inline-block;padding:6px 16px;border-radius:18px;font-weight:700;margin:8px 0 12px}
.ph{background:#fceaea;color:#a23c3c}.pm{background:#fff3db;color:#b96d16}.pl2{background:#eaf6f0;color:#34765d}.ws{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:8px 0 12px}
.wc{background:#f6f1fa;border:1px solid #e4d7ed;border-radius:8px;padding:8px;text-align:center}.wc.on{border:2px solid #8a5aa8;background:#efe6f5}.wm{font-size:10px;font-weight:700;color:#766c80}.wp{font-size:20px;font-weight:700}.wd{font-size:11px;color:#766c80}
.dg{font-size:11px;color:#4c8b72;font-weight:600}.dr{font-size:11px;color:#b64b4b;font-weight:600}
.rb{background:#f6f1fa;border-left:4px solid #8a5aa8;border-radius:0 8px 8px 0;padding:12px 14px;text-align:left}.rb h5{font-size:13px;color:#4b286d}.rb li{font-size:13px;line-height:1.6}
.ci{display:block;width:100%;height:auto;max-height:none;object-fit:contain;background:#fff;padding:16px;cursor:zoom-in}.cn{color:#665d70;font-size:14px;line-height:1.55;padding:6px 18px 14px;margin:0}
.fn{font-size:12px;color:#766c80;padding:10px 14px;background:#fff;border:1px solid #eadff0;border-radius:8px}
"""

def ccard(title, fn, note):
    p = f"figures/{fn}"
    return ui.card(ui.card_header(title),
        ui.tags.a(ui.tags.img(src=p, class_="ci", alt=title), href=p, target="_blank"),
        ui.p(note, class_="cn"))

def kpi(l, v, s, c=""):
    return ui.div(ui.div(l,class_="kl"), ui.div(v,class_="kv"), ui.div(s,class_="ks"), class_=f"kpi {c}")

def scard(l, v, n):
    return ui.card(ui.h6(l), ui.h2(v), ui.p(n),
        style="border-top:4px solid #8a5aa8!important;min-height:130px")

app_ui = ui.page_navbar(
    ui.nav_panel("Order Risk Predictor", ui.tags.style(CSS),
        ui.div(ui.div(ui.h1("DeliveryRisk AI"), ui.p("Order-level delay prediction · Predict. Explain. Prioritize.")),
               ui.span("● Model active · Threshold 0.37", class_="live"), class_="hero"),
        ui.div(kpi("Total orders","25,000","2023–2024"), kpi("Delayed","77.1%","19,278 orders","r"),
               kpi("Detected","2,980","Threshold 0.37","g"), kpi("Top driver","Port congestion","SHAP 1.107","a"), class_="krow"),
        ui.layout_columns(
            ui.card(ui.card_header("Order profile and conditions"),
                ui.input_select("order","Order profile", CHOICES, selected="0"),
                ui.input_select("mode","Planned shipping mode", ["Air","Ground","Sea"]),
                ui.input_select("cat","Product category", ["Beauty","Electronics","Fashion","Home","Sports"]),
                ui.input_slider("cong","Port congestion index", 0, 100, 50),
                ui.input_slider("rel","Supplier reliability", 70, 100, 85, post="%"),
                ui.input_slider("cost","Shipping cost", 1, 900, 284, pre="$"),
                ui.input_slider("tariff","Tariff rate", 1, 25, 13, post="%"),
                ui.input_action_button("go","Assess Delay Risk", class_="btn btn-primary"),
                ui.p("Remaining inputs come from the selected order profile.", class_="st")),
            ui.card(ui.card_header("Risk assessment"), ui.output_ui("res"), class_="ac"),
            col_widths=(5, 7)),
        ui.p("Supports prioritization only; combine with current shipment data and operational judgment.", class_="fn")),

    ui.nav_panel("Order Intelligence", ui.tags.style(CSS),
        ui.div(kpi("Shipping modes","3","Air, Ground, Sea"), kpi("Regions","5","Global markets"),
               kpi("Countries","15","Brazil highest volume"), kpi("Categories","5","Balanced mix"), class_="krow"),
        ccard("Delivery outcomes","target_distribution.png","77.1% of analyzed orders were delayed."),
        ccard("Delay rate by region","delivery_outcome_by_region.png","Delay rates are similar across regions — the issue is systemic."),
        ccard("On-time rate by country","on_time_delivery_rate_by_country.png","Chile 24.1% leads. India 21.0% is lowest."),
        ccard("Lead time by delivery outcome","lead_time_by_delivery_outcome.png","Delayed orders average 21 days vs 9 for on-time — clearest EDA signal.")),

    ui.nav_panel("Model Performance", ui.tags.style(CSS),
        ui.layout_columns(
            scard("FLAGGED","2,980","Delays correctly identified"),
            scard("MISSED","876","Delays not caught"),
            scard("FALSE ALERTS","567","On-time orders flagged"),
            scard("DETECTION RATE","77.3%","F1 0.805 · F2 0.785"),
            col_widths=(3, 3, 3, 3)),
        ccard("Confusion matrix — threshold 0.37","final_logistic_regression_confusion_matrix.png",
            "F2-tuned threshold prioritises catching delays over minimising false alerts."),
        ccard("Model comparison","model_performance_comparison.png",
            "Logistic Regression selected for best balance of recall, precision and explainability.")),

    ui.nav_panel("Risk Drivers", ui.tags.style(CSS),
        ccard("SHAP feature importance","logistic_regression_shap_summary.png",
            "Port Congestion Index (SHAP 1.107) was substantially more influential "
            "than the remaining predictors. Product price, month, week, and shipping cost provided secondary signals."),
        ui.card(ui.card_header("Operational interpretation"),
            ui.tags.ol(
                ui.tags.li(ui.tags.strong("Monitor port congestion closely. "), "It was the strongest predictive signal in the analysis."),
                ui.tags.li(ui.tags.strong("Seasonality matters. "), "Month and week appear in the top 5 SHAP features."),
                ui.tags.li(ui.tags.strong("No single lever eliminates risk. "), "Review the full order context before deciding."),
                ui.tags.li(ui.tags.strong("Use the predictor tab. "), "The what-if comparison shows how switching mode changes risk for that specific order."),
                style="padding-left:18px;line-height:1.9;font-size:13px;color:#374151;"),
            ui.hr(),
            ui.p("SHAP values show predictive associations, not causal relationships.", class_="st"))),

    title="DeliveryRisk AI", selected="Order Risk Predictor", fillable=False)

def server(input, output, session):

    @reactive.effect
    @reactive.event(input.order)
    def sync():
        r = df.loc[int(input.order())]
        ui.update_select("mode",   selected=str(r["Shipping_Mode"]),    session=session)
        ui.update_select("cat",    selected=str(r["Product_Category"]), session=session)
        ui.update_slider("cong",   value=round(float(r["Port_Congestion_Index"])), session=session)
        ui.update_slider("rel",    value=round(float(r["Supplier_Reliability"])),  session=session)
        ui.update_slider("cost",   value=round(float(r["Shipping_Cost"])),         session=session)
        ui.update_slider("tariff", value=round(float(r["Tariff_Rate"]) * 100),     session=session)

    @render.ui
    @reactive.event(input.go)
    def res():
        base = df.loc[[int(input.order())], fcols].copy()
        def prob(mode):
            s = base.copy()
            s["Shipping_Mode"]=mode; s["Product_Category"]=input.cat()
            s["Port_Congestion_Index"]=input.cong(); s["Supplier_Reliability"]=input.rel()
            s["Shipping_Cost"]=input.cost(); s["Tariff_Rate"]=input.tariff()/100
            return float(mdl.predict_proba(pre.transform(s))[0, pidx])

        p = prob(input.mode())
        modes = {m: prob(m) for m in ["Air","Ground","Sea"]}

        if p >= .70:
            pill,lbl,pri,acts = "ph","HIGH RISK","Review immediately.",[
                "Confirm carrier and port status.",
                "Explore routing or fulfillment alternatives.",
                "Prepare proactive customer communication."]
        elif p >= thr:
            pill,lbl,pri,acts = "pm","ELEVATED RISK","Prioritize for review.",[
                "Verify milestones and carrier updates.",
                "Monitor congestion and supplier status.",
                "Confirm contingency options are available."]
        else:
            pill,lbl,pri,acts = "pl2","LOWER RISK","Continue routine monitoring.",[
                "Track through standard operational controls.",
                "Reassess if conditions materially change."]

        sigs = (["High port congestion — above dataset average (50)."] if input.cong()>=70 else []) + \
               (["Supplier reliability below typical level."]           if input.rel()<80   else []) + \
               (["Shipping cost above dataset average ($284)."]         if input.cost()>500 else []) + \
               (["Tariff rate near upper end of observed range."]       if input.tariff()>=20 else []) \
               or ["Operating conditions are near dataset averages."]

        def wcard(m):
            d = modes[m] - p
            is_cur = m == input.mode()
            if is_cur:
                dt, dc = "current mode", "wd"
            elif d < 0:
                dt, dc = f"▼ {abs(d):.0%} lower risk", "dg"
            else:
                dt, dc = f"▲ {d:.0%} higher risk", "dr"
            return ui.div(
                ui.div(m, class_="wm"),
                ui.div(f"{modes[m]:.0%}", class_="wp"),
                ui.div(dt, class_=dc),
                class_=f"wc {'on' if is_cur else ''}")

        return ui.div(
            ui.div("Predicted delay probability", class_="pl"),
            ui.div(f"{p:.1%}", class_="pn"),
            ui.div(lbl, class_=f"rp {pill}"),
            ui.p("Mode comparison — same order, different shipping mode:",
                 style="font-size:11px;font-weight:600;color:#4b286d;margin:4px 0 6px;text-align:left;"),
            ui.div(wcard("Air"), wcard("Ground"), wcard("Sea"), class_="ws"),
            ui.div(ui.tags.h5(pri), ui.tags.ul(*[ui.tags.li(a) for a in acts]),
                   ui.tags.hr(), ui.tags.h5("Scenario signals"),
                   ui.tags.ul(*[ui.tags.li(s) for s in sigs]), class_="rb"),
            ui.p("Supports prioritisation only. Combine with current shipment data and judgement.",
                 class_="st", style="margin-top:8px;"),
            class_="pw")

app = App(app_ui, server, static_assets={"/": WWW, "/figures": FIGS})
