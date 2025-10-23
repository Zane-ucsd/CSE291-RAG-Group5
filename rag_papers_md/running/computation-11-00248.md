<!-- image -->

<!-- image -->

Article

## Effects of Running in Minimal, Maximal and Conventional Footwear on Tibial Stress Fracture Probability: An Examination Using Finite Element and Probabilistic Analyses

Jonathan Sinclair 1, * and Paul John Taylor 2

- 1 Research Centre for Applied Sport, Physical Activity and Performance, School of Health, Social Work &amp; Sport, University of Central Lancashire, Lancashire PR1 2HE, UK
- 2 School of Psychology and Humanities, University of Central Lancashire, Lancashire PR1 2HE, UK; pjtaylor@uclan.ac.uk
* Correspondence: jksinclair@uclan.ac.uk

Abstract: This study examined the effects of minimal, maximal and conventional running footwear on tibial strains and stress fracture probability using finite element and probabilistic analyses. The current investigation examined fifteen males running in three footwear conditions (minimal, maximal and conventional). Kinematic data were collected during overground running at 4.0 m/s using an eight-camera motion-capture system and ground reaction forces using a force plate. Tibial strains were quantified using finite element modelling and stress fracture probability calculated via probabilistic modelling over 100 days of running. Ninetieth percentile tibial strains were significantly greater in minimal (4681.13 µε ) ( p &lt; 0.001) and conventional (4498.84 µε ) ( p = 0.007) footwear compared to maximal (4069.65 µε ). Furthermore, tibial stress fracture probability was significantly greater in minimal footwear (0.22) ( p = 0.047) compared to maximal (0.15). The observations from this investigation show that compared to minimal footwear, maximal running shoes appear to be effective in attenuating runners' likelihood of developing a tibial stress fracture.

Keywords: biomechanics; finite element analysis; footwear; simulation; probabilistic modelling

## 1. Introduction

Running is a highly accessible exercise modality associated with a plethora of physiological [1] and psychological [2] benefits. However, running is also associated with a very high incidence of chronic pathologies [3], with as many as 20-80% of runners experiencing such pathologies annually [4]. Bone stress fractures represent one of the most commonly occurring chronic injuries in runners, accounting for as many as 30% of all running-related musculoskeletal injuries [5]. The tibia has long been regarded as the most vulnerable site of stress fractures [6,7], with as many as 74% of all such injuries being observed at this location [8]. Tibial stress fractures typically occur at the anterior diaphyseal region of this bone [9]. Stress fractures are particularly problematic pathologies owing to their lengthy recovery period and high probability of re-injury [10].

As a cyclical activity, running imposes continuous loads onto the skeletal system, which has the capacity to initiate bone fatigue [11]. Strain is considered to be the closest analogue for actual structural damage to the bone itself [12]. As in vivo strains during running have been shown to be considerably lower than the ultimate strength of bone, stress fracture pathologies are considered to be representative of a mechanical fatigue phenomenon [13], often expressed as an inverse power law association [14]. Stress fractures transpire due to the accrual of microscopic damage within the bony matrix [15]. Permitting sufficient rest between each running exposure allows time for bone remodelling, which may enhance bone integrity [16]. However, if the rate of damage accrual is greater than that of bone remodelling and adaptation, small cracks may materialize in the bony matrix,

<!-- image -->

Citation: Sinclair, J.; Taylor, P .J. Effects of Running in Minimal, Maximal and Conventional Footwear on Tibial Stress Fracture Probability: An Examination Using Finite Element and Probabilistic Analyses. Computation 2023 , 11 , 248. https://doi.org/10.3390/ computation11120248

Academic Editors: Yudong Zhang and Francesco Cauteruccio

Received: 29 September 2023 Revised: 22 November 2023 Accepted: 29 November 2023 Published: 6 December 2023

<!-- image -->

Copyright: © 2023 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (https:// creativecommons.org/licenses/by/ 4.0/).

which proliferates into stress fractures [17]. Importantly, when the tibia experiences low strain magnitudes, damage accumulation is reduced, and the tissue is afforded a greater duration to repair microcracks; yet with high strains, the degree of damage accretion exceeds the repair and adaptation process [18]. Therefore, ascertaining tibial loading patterns that attenuate strain magnitudes during running may aid in the prevention of stress fracture pathologies.

Running shoes serve as the principal interface connecting the foot and ground and have thus been posited as a pivotal mechanism that may influence the biomechanical factors associated with the aetiology of chronic injuries [19]. Modern footwear (henceforth termed conventional footwear) typically feature a high degree of midsole cushioning, particularly in the rear portion of the shoe, stability and motion control technology designed to reduce rearfoot eversion and arch support systems. In addition to conventional footwear models, footwear manufacturers have introduced running shoes with varying levels of midsole cushioning, presenting both minimal and maximal running shoe options [19]. Minimal running shoes are characterized by a low or zero heel-toe drop, enhanced midsole flexibility and reduced mass [20]. On the other hand, maximal running shoes, despite featuring a low heel-toe drop, incorporate a significantly greater amount of midsole cushioning, spanning the entire length of the shoe [19].

Tibial accelerations and the loading rate of the vertical ground reaction force are frequently utilized as proxy indicators for tibial loading and have long been proposed as potential contributors to the development of tibial stress fractures [21]. Substantial research interest has been directed towards examining the impact of minimal and maximal running shoes on tibial accelerations and vertical loading rates during running. It has been observed that minimal running shoes are linked to heightened vertical loading rates and tibial accelerations in comparison to both traditional [19,22] and maximal running shoes [19,22,23]. However, no significant disparities in vertical loading rates and tibial accelerations have been identified between maximal and conventional running shoes [19,22-24].

Recent evidence has shown that surrogate measures, such as tibial acceleration and loading rates of the vertical ground reaction force, are not representative of tibial bone loading in running [21]. Finite element modelling has been shown to provide more realistic estimates of in vivo tibial bone strains [25], directly linked to the aetiology of stress fractures [12]. Indicating that this technique can be utilized to make informed predictions of the damage potential. Significant advances in finite element analyses made in recent years now allow computational probabilistic modelling of the tibia to be undertaken [25,26] in order to quantify the probability of tibial stress fractures in runners utilizing different footwear modalities. However, neither of the aforementioned approaches has been utilized to examine differences between minimal, maximal and conventional running shoes during running.

Therefore, the aim of this study is to investigate the effects of minimal, maximal and conventional running footwear on tibial strains and stress fracture probability via a collective finite element analysis and computational probabilistic modelling-based approach. The findings from this investigation will yield new information regarding the effects of minimal, maximal and conventional footwear on tibial strains during running, but also on longitudinal stress fracture probability. This investigation hypothesizes that minimal footwear will increase tibial strains and tibial stress fracture probability in relation to both conventional and maximal footwear.

## 2. Materials and Methods

## 2.1. Participants

Fifteen males who habitually ran using conventional footwear volunteered for the current investigation. For inclusion in this investigation, participants were required to complete a minimum of 35 km per week of training and be between the ages of 18 and 40. Using data from our previous work [27] with a mean ± SD difference in peak compressive

Computation

2023

,

11

, x FOR PEER REVIEW

3  of  1

Using data from our previous work [27] with a mean ± SD difference in peak compressiv ankle joint contact force of 0.69 ± 0.76 BW between conditions, it was determined that i

ankle joint contact force of 0.69 ± 0.76 BW between conditions, it was determined that in order to achieve 80% power ( b ) for a p -value of 0.05 ( a ), 15 runners would be required for a within-subjects comparison between footwear. All participants were free from pathology at the time of data collection and provided written informed consent in accordance with the principles outlined in the Declaration of Helsinki. The procedure utilized for this investigation was approved by a university ethics committee (STEMH 361). order to achieve 80% power ( β ) for a p -value of 0.05 ( α ), 15 runners would be required fo a within-subjects comparison between footwear. All participants were free from pathol ogy at the time of data collection and provided written informed consent in accordanc with the principles outlined in the Declaration of Helsinki. The procedure utilized for thi investigation was approved by a university ethics committee (STEMH 361).

## 2.2. Footwear 2.2. Footwear

The footwear used during this study consisted of New Balance, 1260 v2 (New Balance, Boston, Massachusetts, United States; termed conventional running shoes); Vibram FiveFingers, ELX (Vibram, Albizzate, Italy; termed minimal); and HOKA OneOne Rapa Nui 2 Tarmac Road (HOKA Goleta, California, United States; termed maximal) (Figure 1a-c). The footwear were scored using the minimalist index of Esculier et al. [20], and their details are shown in Table 1. The footwear used during this study consisted of New Balance, 1260 v2 (New Bal ance, Boston, Massachusetts, United States; termed conventional running shoes); Vibra Five-Fingers, ELX (Vibram, Albizzate, Italy; termed minimal); and HOKA OneOne Rap Nui 2 Tarmac Road (HOKA Goleta, California, United States; termed maximal) (Figur 1a-c). The footwear were scored using the minimalist index of Esculier et al. [20], and thei details are shown in Table 1.

<!-- image -->

) minimal.

Figure 1. Experimental footwear ( a ) conventional, ( b ) maximal and ( c Figure 1. Experimental footwear ( a ) conventional, ( b ) maximal and ( c ) minimal.

Table 1. Study experimental footwear parameters.

|                                              |   Maximal |   Minimal |   Conventional |
|----------------------------------------------|-----------|-----------|----------------|
| Mass (g)                                     |       318 |       167 |            285 |
| Heel thickness (mm)                          |        45 |         7 |             25 |
| Heel-toe drop (mm)                           |         6 |         0 |             14 |
| Esculier et al. (2015) [20] minimalist index |        18 |        92 |             20 |

## 2.3. Procedure

The participants ran at a velocity of 4.0 m/s ( ± 5%), during which they made contact with an embedded piezoelectric force platform (Kistler Instruments Ltd., Winterthur, Switzerland) that recorded data at a rate of 1000 Hz. This was accomplished using their right (dominant) foot. To monitor running velocity, infrared timing gates (Newtest, Oy Koulukatu, Finland) were employed. The stance phase was defined as the time over a vertical ground reaction force (GRF) of 20 N or greater applied to the force platform. Each participant completed five successful trials under each footwear condition, where success was determined via adherence to the specified velocity range, full contact with the force platform and the absence of gait modifications resulting from the experimental conditions. The sequence in which participants ran in each footwear condition was counterbalanced. Kinematic and GRF data were concurrently gathered. Kinematic data were recorded at a rate of 250 Hz using an eight-camera motion analysis system (Qualisys Medical AB, Goteburg, Sweden), and dynamic calibration of the motion capture system was performed before each data collection session.

The body segments were modelled with six degrees of freedom using the calibrated anatomical systems technique [28]. To establish the anatomical frames for the thorax, pelvis, thighs, shanks and feet, retroreflective markers were positioned at specific landmarks such as C7, T12 and the xiphoid process. Bilateral markers were placed on the acromion process, iliac crest, anterior superior iliac spine (ASIS), posterior superior iliac spine, medial and lateral malleoli, medial and lateral femoral epicondyles, greater trochanter, calcaneus, first metatarsal and fifth metatarsal. Carbon-fibre tracking clusters, each consisting of four non-linear retroreflective markers, were applied to the thigh and shank segments (Figure 2a). Additionally, foot segments were tracked using markers on the calcaneus, first and fifth metatarsal, the pelvic segment with PSIS and ASIS markers and the thorax segment with T12, C7 and xiphoid markers. Static calibration trials were conducted to establish a reference between the anatomical markers and the tracking markers/clusters. The midpoints between the malleoli and the femoral epicondyle markers were used to determine the centres of the ankle and knee joints. The hip joint centre was calculated using a regression equation based on the positions of the ASIS markers. Furthermore, the foot segments were tracked via markers on the calcaneus, first metatarsal and fifth metatarsal, while the pelvic segment was tracked using the PSIS and ASIS markers, and the thorax segment was tracked using the T12, C7 and xiphoid markers. The Z (transverse) axis was oriented vertically from the distal segment end to the proximal segment end. The Y (coronal) axis ran from posterior to anterior along the segment, and the X (sagittal) axis orientation was determined using the right-hand rule, with a medial-to-lateral orientation (Figure 2b).

## 2.4. Processing

Dynamic trials were digitized using Qualisys Track Manager (Qualisys Medical AB, Goteburg, Sweden) in order to identify anatomical and tracking markers and then exported as C3D files to Visual 3D (C-Motion, Germantown, MD, USA). All data were linearly normalized to 100% of the stance phase. GRF data and marker trajectories were smoothed with cut-off frequencies of 50 Hz at 12 Hz, respectively, using a low-pass Butterworth

Computation

2023

,

11

4th order zero lag filter. Kinetic and kinematics cut-off frequencies were obtained using residual analysis [29]. , x FOR PEER REVIEW 5  of  19

Figure 2. ( a ) Experimental retroreflective marker positions and ( b ) segment co-ordinate systems (R = right and L = left, TR = trunk, P = pelvis, T = thigh, S = shank and F = foot, X = sagittal plane, Y = coronal plane and Z = transverse plane). Figure 2. ( a ) Experimental retroreflective marker positions and ( b ) segment co-ordinate systems (R = right and L = left, TR = trunk, P = pelvis, T = thigh, S = shank and F = foot, X = sagittal plane, Y = coronal plane and Z = transverse plane).

<!-- image -->

## 2.4. Processing 2.4.1. Running Biomechanics

Dynamic trials were digitized using Qualisys Track Manager (Qualisys Medical AB, Goteburg, Sweden) in order to identify anatomical and tracking markers and then exported as C3D files to Visual 3D (C-Motion, Germantown, MD, USA). All data were lineFollowing the Addison and Lieberman protocol [30], we employed an impulsemomentum modelling method to compute the effective mass (% BW), which was quantified using the equation below:

arly  normalized  to  100%  of  the  stance  phase.  GRF  data  and  marker  trajectories  were smoothed with cut-off frequencies of 50 Hz at 12 Hz, respectively, using a low-pass ButEffective mass = vertical GRF integral/( D foot vertical velocity + gravity × D time)

terworth 4th order zero lag filter. Kinetic and kinematics cut-off frequencies were obtained using residual analysis [29]. 2.4.1. Running Biomechanics Following the Addison and Lieberman protocol [30], we employed an impulse-momentum modelling method to compute the effective mass (% BW), which was quantified using the equation below: Effective mass = vertical GRF integral/( Δ foot vertical velocity + gravity × Δ time) The impact peak was defined in both maximal and traditional running shoes as the The impact peak was defined in both maximal and traditional running shoes as the initial peak in the vertical ground reaction force (GRF). In the case of minimal footwear, where a consistent impact peak was not always present, we applied Lieberman et al.'s [31] guidelines to position the impact peak at the same relative point as observed in the maximal and traditional running shoes. The time to the impact peak ( D time) was measured as the duration from the footstrike to the impact peak. To calculate the integral of the vertical GRF during the impact peak period, a trapezoidal function was utilized. The change in vertical foot velocity ( D foot vertical velocity) was determined as the alteration in vertical foot speed between the footstrike and the impact peak instances [32]. Foot velocity was assessed using the centre of mass of the foot segment in the vertical direction within Visual 3D.

initial peak in the vertical ground reaction force (GRF). In the case of minimal footwear, where a consistent impact peak was not always present, we applied Lieberman et al.'s [31]

guidelines to position the impact peak at the same relative point as observed in the maxi- mal and traditional running shoes. The time to the impact peak (

Δ

time) was measured as

the duration from the footstrike to the impact peak. To calculate the integral of the vertical

GRF during the impact peak period, a trapezoidal function was utilized. The change in vertical foot velocity (

Δ

foot vertical velocity) was determined as the alteration in vertical

6 of 18 foot speed between the footstrike and the impact peak instances [32]. Foot velocity was assessed using the centre of mass of the foot segment in the vertical direction within Visual

3D.

The strike index (%) was calculated as the position of the centre of pressure location at footstrike relative to the total length of the foot [33]. A strike index of 0-33% denotes a rearfoot, 34-67% a midfoot and 68-100% a forefoot strike pattern. The step length (m) was determined as the linear anterior distance in the foot centre of the mass location at the footstrike between the initial and subsequent ipsilateral footfalls [34]. The strike index (%) was calculated as the position of the centre of pressure location at footstrike relative to the total length of the foot [33]. A strike index of 0-33% denotes a rearfoot, 34-67% a midfoot and 68-100% a forefoot strike pattern. The step length (m) was determined as the linear anterior distance in the foot centre of the mass location at the footstrike between the initial and subsequent ipsilateral footfalls [34].

## 2.4.2. Musculoskeletal Simulation 2.4.2. Musculoskeletal Simulation

Data acquired during the stance phase were transferred from Visual 3D to OpenSim 3.3 software (Simtk.org). A validated musculoskeletal model, adjusted to accommodate the individual anthropometric characteristics of each runner, was employed (Figure 3). The model, featuring 12 segments, 19 degrees of freedom and 92 musculotendon actuators [35], was utilized to estimate muscle and joint contact forces within the lower extremity. Initially, a residual reduction algorithm [36] was applied to resolve dynamic inconsistencies between the kinematics of the measured ground reaction force (GRF) and the model. Subsequently, muscle kinetics were quantified using static optimization, following the approach outlined by Steele et al. [37]. Data acquired during the stance phase were transferred from Visual 3D to OpenSim 3.3 software (Simtk.org). A validated musculoskeletal model, adjusted to accommodate the individual anthropometric characteristics of each runner, was employed (Figure 3). The model, featuring 12 segments, 19 degrees of freedom and 92 musculotendon actuators [35], was utilized to estimate muscle and joint contact forces within the lower extremity. Initially, a residual reduction algorithm [36] was applied to resolve dynamic inconsistencies between the kinematics of the measured ground reaction force (GRF) and the model. Subsequently, muscle kinetics were quantified using static optimization, following the approach outlined by Steele et al. [37].

Figure 3. OpenSim musculoskeletal simulation model. Figure 3. OpenSim musculoskeletal simulation model.

<!-- image -->

As muscle forces are the main determinant of joint contact forces [38], following the static optimization process, three-dimensional ankle joint contact forces expressed in the tibial reference frame were calculated via the joint reaction analysis function within OpenSim, using the muscle forces generated from the static optimization process as inputs. The resultant ankle joint contact force was calculated using the three-dimensional Pythagorean theorem, and normalized (BW) ankle joint contact forces in each anatomical

axis (anterior-posterior, axial and medio-lateral) were extracted at the instance of the peak resultant load.

From the above static optimization processes, the normalized muscle forces (BW) that attach to the tibia (biceps femoris long head, biceps femoris short head, extensor digitorum longus, extensor hallucis longus, flexor digitorum longus, flexor hallucis longus, gracilis, rectus femoris, sartorius, semimembranosus, semitendinosus, soleus, tensor fasciae latae, tibialis anterior, tibialis posterior, vastus intermedius, vastus lateralis and vastus medialis) were also extracted at the instance of the peak resultant ankle joint contact force. In addition, other muscles that cross the ankle joint, i.e., medial gastrocnemius, lateral gastrocnemius, peroneus brevis, peroneus longus and peroneus tertius muscle forces at the same relative time point, were also obtained.

Finally, the attachment points of each of the aforementioned muscles (with tibial attachment) onto the tibia were extracted using the OpenSim plugin developed by van Arkel et al. [39] (https://simtk.org/projects/force\_direction, accessed 31 July 2023). Using the same plug-in, anatomically directed muscle forces (BW) onto the tibia at their attachment points for each of the aforementioned muscles were calculated at the instance of the peak resultant ankle joint contact force in all three anatomical directions. Positive values represent anterior, upwards and laterally directed forces onto the tibia.

## 2.4.3. Finite Element Analyses

FEBio software (Musculoskeletal Research Laboratories, Salt Lake City, UT, USA) was used to perform static finite element analysis required to calculate tibial strains. Finite element analyses and all of the applied joint contact/muscle forces, as well as the extracted tibial strains, were undertaken at the instance of peak resultant ankle joint contact force. The tibial surface and trabecular models were created using the statistical shape modelling source code of Keast et al. [40] (https://simtk.org/projects/ssm\_tibia, accessed 25 August 2023). Briefly, Keast et al. [40] created statistical shape modelling source code based on computed tomography scans of 30 cadavers from a generally active population, allowing tibial surfaces segmented and reconstructed into both cortical and trabecular sections to be obtained. Our tibial meshes consisted of 33,004 quadratic tetrahedral elements with an average edge length of 3 mm (Figure 4). In accordance with previous recommendations [41,42], our preliminary mesh sensitivity tests revealed that increasing the number of elements by 50% changed 90th percentile von Mises tibial strains by less than 5%, suggesting adequate mesh convergence. Models were created for each participant scaled axially and radially based on segment length and body mass [36,41] and for each footwear condition based on the applied loads described below. Material properties were assigned based on those adopted previously by Edwards et al. [25], with cortical bone having an elastic modulus of 17.0 GPa and trabecular bone an elastic modulus of 1.0 GPa; both components were ascribed a Poisson's ratio of 0.3 [25].

Each model was assigned boundary conditions that involved full constraints imposed at the tibial plateau (Figure 4a) [43]. Three three-dimensional net ankle joint contact forces obtained from musculoskeletal simulation were applied to the distal tibia (Figure 4b) [43]. Concentrated anatomically directed net muscle forces in each anatomical direction from the muscles obtained from static optimization were also applied at each muscle attachment point on the tibia (Figure 4c). Because some bi-articulating muscles around the ankle joint, such as the gastrocnemius, produce large forces during running, without insertion points onto the tibia itself [43], the contribution of these muscles to tibial strain was attained by calculating a residual ankle joint moment in accordance with Haider et al. [43]. This residual moment was applied to the distal tibia (Figure 4d). In accordance with previous analyses [44], the 50th and 90th percentile von Mises strain ( m# ) and strained volume (mm 3 ), delineated as the sum of the volume experiencing strain magnitudes ≥ 4000 m# , were extracted for analysis.

, x FOR PEER REVIEW

Figure 4. Depiction of finite element model mesh with loading and boundary conditions. The tibial plateau was fully constrained ( a ). Ankle joint contact forces were applied to the distal tibia ( b ); muscle forces (not all shown here) were applied as concentrated forces at their insertion point onto the tibia ( c ), and residual moments were applied at the distal tibia ( d ). Figure 4. Depiction of finite element model mesh with loading and boundary conditions. The tibial plateau was fully constrained ( a ). Ankle joint contact forces were applied to the distal tibia ( b ); muscle forces (not all shown here) were applied as concentrated forces at their insertion point onto the tibia ( c ), and residual moments were applied at the distal tibia ( d ).

<!-- image -->

## Each model was assigned boundary conditions that involved full constraints  im2.4.4. Probabilistic Stress Fracture Model

posed at the tibial plateau (Figure 4a) [43]. Three three-dimensional net ankle joint contact forces obtained from musculoskeletal simulation were applied to the distal tibia (Figure 4b) [43]. Concentrated anatomically directed net muscle forces in each anatomical direction from the muscles obtained from static optimization were also applied at each muscle attachment point on the tibia (Figure 4c). Because some bi-articulating muscles around the ankle joint, such as the gastrocnemius, produce large forces during running, without inWe determined the probability of stress fracture for each participant in each footwear condition firstly by accounting for the daily running distance, which was included in the model as runners completing 5.0 km/day for 100 consecutive days [25,26,41]. The number of loading cycles/footfalls per day in each footwear condition was quantified by dividing the modelled daily running distance by the step length in each footwear outlined in the aforementioned running biomechanics section [45].

sertion points onto the tibia itself [43], the contribution of these muscles to tibial strain was attained by calculating a residual ankle joint moment in accordance with Haider et al. [43]. This residual moment was applied to the distal tibia (Figure 4d). In accordance with previous analyses [44], the 50th and 90th percentile von Mises strain ( µ ε ) and strained volume The likelihood of tibial stress fracture was determined using a probabilistic model of bone damage, repair, and adaptation in accordance with previous analyses [25,26,41]. The fatigue life of the tibial bone was modelled as a function of the standard fatigue equation [46]:

(mm 3 ),  delineated as the sum of the volume experiencing strain magnitudes

≥

4000

µ

ε

,

<!-- formula-not-decoded -->

were extracted for analysis.

where FLT represents the number of tibial loading cycles to failure and D # is the strain range from the finite element analysis. As strain magnitude is zero for some modelled tibial

elements, the maximum strain from the finite element analysis was adopted to represent strain D # . n is representative of the slope of the stressed-life curve of bone, and C is a constant. Carter and Caler [46] observed a slope of n = 6.6 for fatigue damage of bone at strain magnitudes to human locomotion [25,26,41].

As bone adaptation occurs in response to applied loading, an increase in the bone cross-sectional area transpires such that tibial strains are attenuated over time. Taking into account a maximum deposition of lamellar bone accumulation of 4 µ m/day on the periosteum membrane [47], an adaptation function was quantified using equations of beam theory [25,26,41]. The adaptation function was calculated as the ratio of strain following bone accumulation to strain with initially modelled bone geometry. The product of this adaptation function and D # was adopted to ascertain alterations in tibial strains owing to bone adaptation. An equivalent strain ( D # AD) for each element that accounted for adaptation was then determined where tT is the total modelled duration over which bone adaptation occurred, i.e., 100 days [48]:

<!-- formula-not-decoded -->

Furthermore, as there is substantial dispersion in the fatigue life of bone, a common technique in fatigue mechanics utilized to ascertain the probability of bone failure with adaptation ( PfA ) is the Weibull approach [49]. Therefore, a modified Weibull function was utilized that accounted for stressed volume [48]:

<!-- formula-not-decoded -->

Inputs to the above equation were obtained from experimental fatigue testing literature to allow PfA for a specimen with stressed volume Vs (obtained from the finite element meshes) from time zero to t; Vso is the reference stressed volume, tf is the reference time until failure at the applied strain range and number of loading cycles/day and w denotes the degree of scatter in the material.

Since D # ADis not consistent across the entire tibial body, PfA differs from element to element. From the finite element analysis, distinct PfA indices could be quantified for each element. Given k elements, PfA for the entire tibial body was the probability that any one element would fail [50]:

<!-- formula-not-decoded -->

Elements with similar strain magnitudes were grouped together as Taylor and Kuiper [50] showed that eight element groups could be utilized without significant error. The Vs for each of the eight groups was determined by summating the element volumes from each one; then, taking the peak strain values from each group, the above formulae was utilized to determine a singular PfA for the entire tibia.

Much like the fatigue life of bone, there is substantial variability in the duration over which bone microcracks are able to repair. Taylor et al. [48] estimated this time to be 18.5 ± 12.5 days. Therefore, the cumulative probability of bone repair PR was determined by adopting a second Weibull function [48]:

<!-- formula-not-decoded -->

where tr is the reference time for repair, and m articulates the degree of scatter in repair time. Finally, by determining the probability that bone will not repair itself (1 -PR ) and multiplying it by the instantaneous probability of PfA , integration with respect to time yielded the cumulative probability of tibial bone failure with repair and adaptation (PFRA).

## 2.5. Statistical Analyses

Descriptive statistics of means and standard deviations (SD) were calculated for each of the experimental variables and footwear conditions outlined above. To contrast these variables between the three different experimental footwear conditions, within-subjects linear mixed-effects models were adopted utilizing compound symmetry and restricted maximum-likelihood methods, with footwear modelled as a fixed factor and participants representing the random intercept. Effect sizes were calculated using Cohen's d ( d ), which were interpreted as 0.2 = small, 0.5 = medium and 0.8 = large [51]. Statistical significance for all analyses was accepted at the p ≤ 0.05 level and all statistical analyses were conducted using SPSS v27 (IBM, SPSS, Armonk, NY, USA).

## 3. Results

## 3.1. Running Biomechanics (Described in Section 2.4.1)

The strike index was shown to be significantly greater in minimal footwear compared to maximal ( p = 0.004, d = 0.90) and conventional ( p &lt; 0.001, d = 1.27) footwear (Table 2). Step length was also shown to be significantly greater in conventional compared to minimal footwear ( p = 0.023, d = 0.66) (Table 2).

Table 2. Running biomechanics outcomes (mean ± standard deviations) as a function of footwear.

|                    | Maximal   | Maximal   | Minimal   | Minimal   | Conventional   | Conventional   |      |
|--------------------|-----------|-----------|-----------|-----------|----------------|----------------|------|
|                    | Mean      | SD        | Mean      | SD        | Mean           | SD             |      |
| Effective mass (%) | 10.89     | 1.76      | 10.09     | 2.01      | 11.47          | 2.61           |      |
| Strike index (%)   | 17.85     | 3.80      | 34.15     | 19.69     | 14.42          | 9.30           | A, B |
| Step length (m)    | 0.90      | 0.08      | 0.89      | 0.07      | 0.90           | 0.08           | B    |

A=minimal significantly different from maximal. B = minimal significantly different from conventional.

## 3.2. Musculoskeletal Simulation (Described in Section 2.4.2)

## 3.2.1. Ankle Joint Contact Forces and Muscle Forces

Posterior ankle joint contact force was significantly greater in the minimal footwear compared to maximal ( p = 0.012, d = 0.75) (Table 3). Axial contact forces were significantly greater in the minimal compared to maximal ( p = 0.002, d = 1.01) and conventional ( p = 0.013, d = 0.73) footwear (Table 3). Medial ankle joint contact forces were significantly larger in the minimal compared to maximal ( p &lt; 0.001, d = 1.25) and conventional ( p = 0.021, d = 0.67) footwear and in the conventional compared to maximal footwear ( p = 0.012, d = 0.75) (Table 3).

Table 3. Joint contact and muscle forces (mean ± standard deviations) as a function of footwear.

|                                | Maximal   | Maximal   | Minimal   | Minimal   | Conventional   | Conventional   |         |
|--------------------------------|-----------|-----------|-----------|-----------|----------------|----------------|---------|
|                                | Mean      | SD        | Mean      | SD        | Mean           | SD             |         |
| Posterior tibial load (BW)     | 2.61      | 0.60      | 2.97      | 0.60      | 2.78           | 0.69           | A       |
| Axial tibial load (BW)         | 11.29     | 1.03      | 12.06     | 0.93      | 11.50          | 0.98           | A, B    |
| Medial tibial load (BW)        | 1.02      | 0.48      | 1.27      | 0.39      | 1.12           | 0.51           | A, B, C |
| Biceps femoris long head (BW)  | 0.17      | 0.10      | 0.21      | 0.14      | 0.24           | 0.18           | C       |
| Biceps femoris short head (BW) | 0.03      | 0.04      | 0.03      | 0.04      | 0.01           | 0.01           |         |
| Extensor digitorum longus (BW) | 0.16      | 0.15      | 0.18      | 0.20      | 0.19           | 0.20           |         |
| Extensor hallucis longus (BW)  | 0.06      | 0.06      | 0.05      | 0.06      | 0.05           | 0.04           |         |
| Flexor digitorum longus (BW)   | 0.05      | 0.09      | 0.03      | 0.05      | 0.02           | 0.02           |         |
| Flexor hallucis longus (BW)    | 0.07      | 0.14      | 0.07      | 0.13      | 0.07           | 0.13           |         |

Table 3. Cont.

|                            | Maximal   | Maximal   | Minimal   | Minimal   | Conventional   | Conventional   |         |
|----------------------------|-----------|-----------|-----------|-----------|----------------|----------------|---------|
|                            | Mean      | SD        | Mean      | SD        | Mean           | SD             |         |
| Gracilis (BW)              | 0.00      | 0.00      | 0.00      | 0.00      | 0.00           | 0.00           |         |
| Rectus femoris (BW)        | 1.81      | 0.39      | 1.86      | 0.54      | 1.92           | 0.35           |         |
| Sartorius (BW)             | 0.05      | 0.05      | 0.08      | 0.08      | 0.07           | 0.06           |         |
| Semimembranosus (BW)       | 0.35      | 0.20      | 0.32      | 0.25      | 0.28           | 0.20           | C       |
| Semitendinosus (BW)        | 0.04      | 0.03      | 0.02      | 0.03      | 0.02           | 0.03           | C       |
| Soleus (BW)                | 5.31      | 0.66      | 5.25      | 0.45      | 5.33           | 0.63           |         |
| Tensor fasciae latae (BW)  | 0.44      | 0.13      | 0.40      | 0.16      | 0.40           | 0.16           |         |
| Tibialis anterior (BW)     | 0.08      | 0.12      | 0.02      | 0.02      | 0.03           | 0.02           |         |
| Tibialis posterior (BW)    | 1.37      | 0.50      | 1.20      | 0.34      | 1.36           | 0.59           |         |
| Vastus intermedius (BW)    | 1.84      | 0.40      | 1.67      | 0.39      | 1.70           | 0.38           | A, C    |
| Vastus lateralis (BW)      | 2.51      | 0.55      | 2.27      | 0.53      | 2.31           | 0.55           | A, C    |
| Vastus medialis (BW)       | 1.73      | 0.37      | 1.56      | 0.36      | 1.60           | 0.35           | A, C    |
| Lateral gastrocnemius (BW) | 0.58      | 0.38      | 0.65      | 0.41      | 0.54           | 0.41           | B       |
| Medial gastrocnemius (BW)  | 1.05      | 0.56      | 1.86      | 0.49      | 1.32           | 0.60           | A, B, C |
| Peroneus brevis (BW)       | 0.21      | 0.20      | 0.22      | 0.26      | 0.23           | 0.27           |         |
| Peroneus longus (BW)       | 0.97      | 0.46      | 1.15      | 0.36      | 1.12           | 0.40           | A       |
| Peroneus tertius (BW)      | 0.04      | 0.05      | 0.04      | 0.08      | 0.04           | 0.07           |         |

A=minimal significantly different from maximal. B = minimal significantly different from conventional. C = conventional significantly different from maximal.

## 3.2.2. Muscle Forces

Biceps femoris long head force was significantly greater in the conventional footwear compared to maximal ( p = 0.048, d = 0.56) (Table 3). Lateral gastrocnemius force was significantly greater in the minimal footwear compared to conventional ( p = 0.033, d = 0.61) (Table 3). Medial gastrocnemius forces were significantly larger in the minimal compared to maximal ( p &lt; 0.001, d = 1.47) and conventional ( p = 0.009, d = 0.78) footwear and in the conventional compared to maximal footwear ( p = 0.021, d = 0.67) (Table 3). Semimembranosus forces were significantly greater in the conventional footwear compared to maximal ( p = 0.016, d = 0.71) and semitendinosus force in the maximal footwear compared to conventional ( p = 0.016, d = 0.72) (Table 3).

Vastus intermedius, vastus lateralis and vastus medialis forces were significantly greater in the maximal compared to minimal ( p = 0.037, d = 0.59, p = 0.045, d = 0.57 and p = 0.027, d = 0.63) and conventional ( p = 0.009, d = 0.78, p = 0.009, d = 0.772 and p = 0.012, d = 0.74) footwear (Table 3). Peroneus longus force was significantly greater in minimal compared to maximal footwear ( p = 0.038, d = 0.59) (Table 3).

## 3.2.3. Anatomically Directed Muscle Forces Onto the Tibia

Vertically directed biceps femoris long head force was significantly greater in the traditional footwear compared to maximal ( p = 0.045, d = 0.59) (Table 4). Posteriorly and vertically directed semimembranosus forces were significantly greater in the maximal compared to traditional footwear ( p = 0.029, d = 0.62 and p = 0.016, d = 0.72) (Table 4). Posteriorly and vertically directed semitendinosus force was significantly greater in the maximal compared to traditional footwear ( p = 0.012, d = 0.76 and p = 0.025, d = 0.66) (Table 4). Posteriorly directed tensor fasciae latae force was significantly greater in the maximal compared to minimal footwear ( p = 0.004, d = 0.91) (Table 4).

Table 4. Anatomically directed muscle forces onto the tibia (mean ± standard deviations) as a function of footwear ( A/P = anterior-posterior, AX = axial and M/L = medial-lateral ).

|                           |     | Maximal   | Maximal   | Minimal   | Minimal   | Conventional   | Conventional   |    |
|---------------------------|-----|-----------|-----------|-----------|-----------|----------------|----------------|----|
|                           |     | Mean      | SD        | Mean      | SD        | Mean           | SD             |    |
| Biceps femoris long head  | A/P | - 0.13    | 0.07      | - 0.15    | 0.10      | - 0.18         | 0.12           |    |
|                           | AX  | 0.11      | 0.06      | 0.15      | 0.10      | 0.16           | 0.13           | C  |
|                           | M/L | - 0.02    | 0.01      | - 0.02    | 0.02      | - 0.03         | 0.02           |    |
| Biceps femoris short head | A/P | - 0.01    | 0.02      | - 0.01    | 0.01      | - 0.01         | 0.01           |    |
| Biceps femoris short head | AX  | 0.02      | 0.03      | 0.02      | 0.03      | 0.01           | 0.01           |    |
| Biceps femoris short head | M/L | 0.00      | 0.00      | 0.00      | 0.00      | 0.00           | 0.00           |    |
| Extensor digitorum longus | A/P | 0.05      | 0.04      | 0.04      | 0.07      | 0.08           | 0.09           |    |
| Extensor digitorum longus | AX  | - 0.10    | 0.07      | - 0.09    | 0.07      | - 0.12         | 0.12           |    |
| Extensor digitorum longus | M/L | 0.09      | 0.14      | 0.12      | 0.19      | 0.10           | 0.14           |    |
| Extensor hallucis longus  | A/P | 0.04      | 0.04      | 0.03      | 0.04      | 0.03           | 0.03           |    |
| Extensor hallucis longus  | AX  | - 0.04    | 0.04      | - 0.03    | 0.03      | - 0.04         | 0.03           |    |
| Extensor hallucis longus  | M/L | 0.02      | 0.03      | 0.02      | 0.04      | 0.01           | 0.01           |    |
| Flexor digitorum longus   | A/P | 0.02      | 0.05      | 0.01      | 0.03      | 0.01           | 0.01           |    |
| Flexor digitorum longus   | AX  | - 0.04    | 0.08      | - 0.02    | 0.04      | - 0.02         | 0.02           |    |
| Flexor digitorum longus   | M/L | 0.00      | 0.01      | 0.00      | 0.01      | 0.00           | 0.00           |    |
| Flexor hallucis longus    | A/P | 0.03      | 0.07      | 0.03      | 0.07      | 0.03           | 0.06           |    |
| Flexor hallucis longus    | AX  | - 0.07    | 0.12      | - 0.06    | 0.11      | - 0.06         | 0.11           |    |
| Flexor hallucis longus    | M/L | 0.01      | 0.02      | 0.01      | 0.02      | 0.00           | 0.01           |    |
| Gracilis (BW)             | A/P | 0.00      | 0.00      | 0.00      | 0.00      | 0.00           | 0.00           |    |
| Gracilis (BW)             | AX  | 0.00      | 0.00      | 0.00      | 0.00      | 0.00           | 0.00           |    |
| Gracilis (BW)             | M/L | 0.00      | 0.00      | 0.00      | 0.00      | 0.00           | 0.00           |    |
| Rectus femoris (BW)       | A/P | 0.24      | 0.06      | 0.27      | 0.07      | 0.27           | 0.06           |    |
| Rectus femoris (BW)       | AX  | 1.78      | 0.39      | 1.83      | 0.53      | 1.89           | 0.35           |    |
| Rectus femoris (BW)       | M/L | 0.18      | 0.04      | 0.18      | 0.05      | 0.19           | 0.03           |    |
| Sartorius (BW)            | A/P | - 0.02    | 0.02      | - 0.03    | 0.03      | - 0.03         | 0.03           |    |
| Sartorius (BW)            | AX  | 0.04      | 0.05      | 0.08      | 0.07      | 0.06           | 0.06           |    |
| Sartorius (BW)            | M/L | 0.00      | 0.00      | 0.00      | 0.00      | 0.00           | 0.00           |    |
| Semimembranosus           | A/P | - 0.25    | 0.13      | - 0.22    | 0.16      | - 0.20         | 0.14           | C  |
| Semimembranosus           | AX  | 0.24      | 0.15      | 0.24      | 0.19      | 0.20           | 0.15           | C  |
| Semimembranosus           | M/L | 0.01      | 0.00      | 0.01      | 0.01      | 0.01           | 0.01           |    |
|                           | A/P | - 0.03    | 0.02      | - 0.02    | 0.02      | - 0.01         | 0.02           | C  |
|                           | AX  | 0.02      | 0.02      | 0.02      | 0.02      | 0.01           | 0.02           | C  |
|                           | M/L | 0.00      | 0.00      | 0.00      | 0.00      | 0.00           | 0.00           |    |
|                           | A/P | - 0.65    | 0.10      | - 0.62    | 0.09      | - 0.64         | 0.10           |    |
|                           | AX  | - 5.26    | 0.65      | - 5.21    | 0.45      | - 5.29         | 0.62           |    |
|                           | M/L | - 0.19    | 0.08      | - 0.20    | 0.06      | - 0.19         | 0.07           |    |
|                           | A/P | - 0.02    | 0.01      | - 0.01    | 0.01      | - 0.02         | 0.01           | A  |
| Tensor fasciae latae      | AX  | 0.44      | 0.13      | 0.39      | 0.15      | 0.40           | 0.16           |    |
| Tensor fasciae latae      | M/L | 0.07      | 0.02      | 0.07      | 0.03      | 0.07           | 0.03           |    |

Table 4. Cont.

|                    |     | Maximal   | Maximal   | Minimal   | Minimal   | Conventional   | Conventional   |      |
|--------------------|-----|-----------|-----------|-----------|-----------|----------------|----------------|------|
|                    |     | Mean      | SD        | Mean      | SD        | Mean           | SD             |      |
| Tibialis anterior  | A/P | 0.05      | 0.08      | 0.01      | 0.02      | 0.02           | 0.02           |      |
| Tibialis anterior  | AX  | - 0.04    | 0.05      | - 0.01    | 0.01      | - 0.02         | 0.01           | A, B |
| Tibialis anterior  | M/L | 0.03      | 0.08      | 0.01      | 0.01      | 0.00           | 0.01           |      |
| Tibialis posterior | A/P | 0.52      | 0.19      | 0.48      | 0.16      | 0.52           | 0.22           |      |
|                    | AX  | - 1.26    | 0.47      | - 1.09    | 0.32      | - 1.25         | 0.56           |      |
|                    | M/L | 0.11      | 0.05      | 0.10      | 0.04      | 0.10           | 0.04           |      |
| Vastus intermedius | A/P | 0.25      | 0.05      | 0.25      | 0.04      | 0.24           | 0.05           |      |
|                    | AX  | 1.82      | 0.39      | 1.64      | 0.38      | 1.67           | 0.38           | A, C |
|                    | M/L | 0.17      | 0.04      | 0.15      | 0.04      | 0.15           | 0.03           | A, C |
| Vastus lateralis   | A/P | 0.34      | 0.07      | 0.33      | 0.06      | 0.32           | 0.07           |      |
|                    | AX  | 2.47      | 0.54      | 2.23      | 0.52      | 2.27           | 0.54           | A, C |
|                    | M/L | 0.32      | 0.07      | 0.29      | 0.07      | 0.30           | 0.07           | A, C |
| Vastus medialis    | A/P | 0.26      | 0.05      | 0.25      | 0.04      | 0.24           | 0.05           |      |
|                    | AX  | 1.71      | 0.37      | 1.54      | 0.36      | 1.58           | 0.34           | A, C |
|                    | M/L | 0.10      | 0.02      | 0.09      | 0.02      | 0.10           | 0.02           | A, C |

A=minimal significantly different from maximal. B = minimal significantly different from conventional. C = conventional significantly different from maximal.

Tibialis anterior force in the downwards direction was significantly greater in maximal ( p = 0.045, d = 0.56) and conventional ( p = 0.039, d = 0.57) footwear compared to minimal (Table 4). Vertically directed forces at the vastus intermedius ( p = 0.035, d = 0.60 and p = 0.009 d = 0.76), vastus lateralis ( p = 0.043, d = 0.57 and p = 0.01 d = 0.75) and vastus medialis ( p = 0.026, d = 0.65 and p = 0.013 d = 0.72) were significantly greater in the maximal compared to minimal and conventional footwear (Table 4). Laterally directed forces at the vastus intermedius ( p = 0.037, d = 0.59 and p = 0.01 d = 0.75), vastus lateralis ( p = 0.045, d = 0.56 and p = 0.01 d = 0.75) and vastus medialis ( p = 0.027, d = 0.64 and p = 0.013 d = 0.72) were also significantly greater in the maximal compared to minimal and conventional footwear (Table 4).

## 3.3. Finite Element Analysis (Described in Section 2.4.3)

Fiftieth percentile strain was significantly greater in the minimal ( p &lt; 0.001, d = 1.18) and conventional ( p = 0.006, d = 0.83) footwear compared to maximal (Table 5; Figure 5). Ninetieth percentile strain was significantly greater in the minimal ( p &lt; 0.001, d = 1.19) and conventional ( p = 0.007, d = 0.84) footwear compared to maximal (Table 5; Figure 5). Strained volume was significantly greater in the minimal ( p = 0.019, d = 0.69) and conventional ( p = 0.043, d = 0.57) footwear compared to maximal (Table 5).

Table 5. Finite element analysis outcomes (mean ± standard deviations) as a function of footwear.

|                                         | Maximal   | Maximal   | Minimal   | Minimal   | Conventional   | Conventional   |      |
|-----------------------------------------|-----------|-----------|-----------|-----------|----------------|----------------|------|
|                                         | Mean      | SD        | Mean      | SD        | Mean           | SD             |      |
| 90th percentile Von Mises strain ( µε ) | 4069.65   | 852.14    | 4681.13   | 675.55    | 4498.84        | 975.36         | A, C |
| 50th percentile Von Mises strain ( µε ) | 2264.47   | 473.66    | 2604.42   | 375.56    | 2502.89        | 541.93         | A, C |
| Strained Volume (mm 3 )                 | 1305.45   | 1653.50   | 2670.33   | 3143.12   | 2444.31        | 3038.11        | A, C |

A=minimal significantly different from maximal. B = minimal significantly different from conventional. C = conventional significantly different from maximal.

Computation

2023

,

11

, x FOR PEER REVIEW

, x FOR PEER REVIEW

<!-- image -->

Figure 5.

Representative tibial strain distribution on the tibia.

Figure 5. Representative tibial strain distribution on the tibia. Figure 5. Representative tibial strain distribution on the tibia.

3.4. Stress Fracture Probability (Described in Section 2.4.4)

3.4. Stress Fracture Probability (Described in Section 2.4.4) 3.4. Stress Fracture Probability (Described in Section 2.4.4) Daily loading cycles were shown to be significantly greater in the minimal compared

Daily loading cycles were shown to be significantly greater in the minimal compared to conventional footwear ( p = 0.023, d = 0.66). Stress fracture probability was significantly greater in the minimal footwear ( p = 0.047, d = 0.56) compared to maximal (Table 6; Figure Daily loading cycles were shown to be significantly greater in the minimal compared to conventional footwear ( p = 0.023, d = 0.66). Stress fracture probability was significantly greater in the minimal footwear ( p = 0.047, d = 0.56) compared to maximal (Table 6; Figure 6). to conventional footwear ( p = 0.023, d = 0.66). Stress fracture probability was significantly greater in the minimal footwear ( p = 0.047, d = 0.56) compared to maximal (Table 6; Figure 6).

6).

Figure 6. Average probabilities of failure (PFRA) in each footwear condition across 100 days of runFigure 6. Average probabilities of failure (PFRA) in each footwear condition across 100 days of running. Figure 6. Average probabilities of failure (PFRA) in each footwear condition across 100 days of running.

<!-- image -->

ning.

14  of  19

Table 6. Probability of failure (mean ± standard deviations) as a function of footwear.

|                                 | Maximal   | Maximal   | Minimal   | Minimal   | Conventional   | Conventional   |    |
|---------------------------------|-----------|-----------|-----------|-----------|----------------|----------------|----|
|                                 | Mean      | SD        | Mean      | SD        | Mean           | SD             |    |
| Daily loading cycles            | 2799.61   | 257.08    | 2835.22   | 255.902   | 2792.33        | 247.41         | B  |
| Probability of failure (PF RA ) | 0.15      | 0.17      | 0.22      | 0.18      | 0.18           | 0.21           | A  |

A=minimal significantly different from maximal. B = minimal significantly different from conventional.

## 4. Discussion

The aim of the current investigation was to examine the effects of minimal, maximal and conventional running footwear on tibial strains and stress fracture probability using a cumulative finite element analysis and computational modelling-based approach. This is the first examination of the effects of minimal, maximum and conventional footwear using a concurrent approach of the aforementioned techniques and may therefore yield new information regarding the effects of minimal, maximal and conventional footwear on tibial strains during running, but also on longitudinal stress fracture probability. This investigation tested the hypothesis that minimal footwear will increase tibial strains and tibial stress fracture probability compared to both conventional and maximal footwear.

The current study showed, using musculoskeletal simulation, that ankle joint contact forces in the posterior, axial and medial directions were significantly greater in minimal footwear. To the authors' knowledge, this investigation is the first to examine threedimensional ankle joint contact loading in these footwear; however, this observation concurs with previous analyses adopting external indices as pseudo-measures of tibial loading [19,22-24]. The strike index denoted that the minimal footwear was associated with a significantly more anterior and, on average, midfoot strike location [33]. A more anterior strike location has been shown to increase the ankle plantarflexion moment and plantar flexor muscle forces [21]. Therefore, the greater forces that were observed in the minimal footwear condition in the muscles crossing the ankle joint, i.e., medial and lateral gastrocnemius, were to be expected, and it is proposed that the increased ankle joint contact forces were mediated as a function of these enhanced muscle kinetics [46].

Stress fractures are representative of a mechanical fatigue phenomenon, whereby highmagnitude strains without sufficient rest between loading exposures are responsible for the initiation and progression of microscopic damage in the bony matrix, which ultimately results in injury [17]. It is notable therefore in partial agreement with our hypotheses, that both strain magnitude and strained volume were significantly greater in the minimal and conventional footwear compared to maximal. It is proposed that this observation is related primarily to the aforementioned increases in three-dimensional ankle joint contact forces in the minimal footwear and medially directed contact forces in the conventional footwear. Furthermore, as the plantar flexor muscle forces, which facilitate posterior tibial bending, were significantly greater in the minimal and conventional footwear compared to maximal, it would also be expected that tibial strains due to bending would also be increased. Owing to the association between tibial strains and tibial bone damage, this investigation shows that minimal and conventional footwear appear to place runners at increased risk from the mechanical parameters linked to the aetiology of tibial stress fractures [12].

Importantly, this investigation showed that tibial stress fracture probability was significantly greater in the minimal compared to maximal footwear. Taking into account the parameters included in the probabilistic model, such increases were mediated firstly as a function of the significantly greater tibial strains allied with the increased number of daily loading cycles required to complete the required modelled daily distance. This investigation therefore indicates that minimal footwear places runners at a significantly increased risk from tibial stress fractures in comparison with maximal running shoes. Taking into account the high incidence of tibial stress fractures in runners [6,7], their debilitating and painful presentation, as well their high rate of re-occurrence [9], the findings from this

study indicate that compared to minimal footwear, maximal running shoes appear to be effective in attenuating runners' likelihood of developing a tibial stress fracture.

Scrutinization of the ankle joint contact forces against previous analyses showed that they were similar to other analyses using musculoskeletal simulation techniques at similar running velocities [25,26]. Similarly, the strains experienced by the tibia were also comparable to those observed by previous analyses at the same or similar running velocities [26]. Finally, in relation to the tibial stress fracture probabilities, our values are consistent with other probabilistically derived failure rates at similar running speeds [25,26]; and importantly, the acceleration of risk over the first 40 days, as well as the overall incidence, is also consistent with the epidemiological literature for runners experiencing tibial stress fractures [52]. However, like all research, this investigation is not without limitations. Firstly, whilst our finite element model was scaled to individual participant dimensions, person-specific bone geomorphologies and, indeed, material properties were not considered. As both tibial bone geometry and density influence tibial strains [42,53], the model adopted within this study may not have quantified tibial strains with complete accuracy. Importantly, sex is considered to be an independent risk factor for tibial stress fractures, and epidemiological literature has shown that females are at four times greater risk compared to males [52]. It is not known whether our findings are generalizable to female runners, and it is therefore recommended that the effects of minimal, maximal and conventional footwear also be examined using probabilistic tibial stress fracture modelling in female runners. Finally, the lack of mechanical testing that may have yielded important information regarding key footwear biomechanical indices such as longitudinal bending stiffness, flexibility, friction and midsole hardness may also serve as a drawback to this study. Future analyses may wish to examine these parameters to elucidate further mechanistic information regarding susceptibility to chronic pathologies when running in minimal and maximal footwear.

## 5. Conclusions

In conclusion, no comparison of conventional, minimal and maximal footwear has previously been undertaken using cumulative finite element and probabilistic analyses of tibial stress fractures. Therefore, this study adds to the present clinical and scientific knowledge base in footwear biomechanics by examining the effects of conventional, minimal and maximal footwear on tibial stress fracture probability in in runners. In the minimal and conventional conditions, tibial strains and strained volumes were increased statistically compared to maximal footwear. Furthermore, in minimal footwear, tibial stress fracture probability was significantly increased compared to the maximal footwear. The current investigation importantly shows that compared to minimal footwear, maximal running shoes appear to be effective in attenuating runners' likelihood of developing a tibial stress fracture.

Author Contributions: Conceptualization, J.S. and P.J.T.; methodology, J.S.; formal analysis, J.S. and P.J.T.; investigation, J.S. and P.J.T.; data curation, J.S.; writing-original draft preparation, J.S. and P.J.T.; writing-review and editing, J.S. and P.J.T. All authors have read and agreed to the published version of the manuscript.

Funding: This research received no external funding.

Institutional Review Board Statement: The methods employed for this study received approval from a university ethical committee (REF: 361).

Informed Consent Statement: Informed consent was obtained from all subjects involved in the study.

Data Availability Statement: Data are contained within the article.

Acknowledgments: We would like to sincerely thank Brent Edwards from the University of Calgary for his help with this work, which could not have happened without his unwavering support and assistance.

## Conflicts of Interest: The authors declare no conflict of interest.

## References

1. Lee, D.-C.; Pate, R.R.; Lavie, C.J.; Sui, X.; Church, T.S.; Blair, S.N. Leisure-Time Running Reduces all-Cause and Cardiovascular Mortality Risk. J. Am. Coll. Cardiol. 2014 , 64 , 472-481. [CrossRef] [PubMed]
2. Pereira, H.V.; Palmeira, A.L.; Encantado, J.; Marques, M.M.; Santos, I.; Carraça, E.V.; Teixeira, P.J. Systematic Review of Psychological and Behavioral Correlates of Recreational Running. Front. Psychol. 2021 , 12 , 1162. [CrossRef]
3. van Gent, R.N.; Siem, D.; van Middelkoop, M.; van Os, A.G.; A Bierma-Zeinstra, S.M.; Koes, B.W.; E Taunton, J. Incidence and determinants of lower extremity running injuries in long distance runners: A systematic review. Br. J. Sports Med. 2007 , 41 , 469-480. [CrossRef]
4. Aicale, R.; Tarantino, D.; Maffulli, N. Overuse injuries in sport: A comprehensive overview. J. Orthop. Surg. Res. 2018 , 13 , 309. [CrossRef] [PubMed]
5. Fredericson, M.; Jennings, F.; Beaulieu, C.; Matheson, G.O. Stress fractures in athletes. Top Magn Reson Imaging. 2006 , 17 , 309-325. [CrossRef]
6. Milner, C.E.; Ferber, R.; Pollard, C.D.; Hamill, J.; Davis, I.S. Biomechanical Factors Associated with Tibial Stress Fracture in Female Runners. Med. Sci. Sports Exerc. 2006 , 38 , 323-328. [CrossRef]
7. E Taunton, J.; Ryan, M.B.; Clement, D.B.; McKenzie, D.C.; Lloyd-Smith, D.R.; Zumbo, B.D. A retrospective case-control analysis of 2002 running injuries. Br. J. Sports Med. 2002 , 36 , 95-101. [CrossRef]
8. Armstrong, D.W.; Rue, J.-P.H.; Wilckens, J.H.; Frassica, F.J. Stress fracture injury in young military men and women. Bone 2004 , 35 , 806-816. [CrossRef]
9. Robertson, G.A.J.; Wood, A.M. Lower limb stress fractures in sport: Optimising their management and outcome. World J. Orthop. 2017 , 8 , 242-255. [CrossRef] [PubMed]
10. Robertson, G.A.J.; Wood, A.M. Return to sports after stress fractures of the tibial diaphysis: A systematic review. Br. Med. Bull. 2015 , 114 , 95-111. [CrossRef]
11. Gallagher, S.; Schall, M.C., Jr. Musculoskeletal disorders as a fatigue failure process: Evidence, implications and research needs. Ergonomics 2017 , 60 , 255-269. [CrossRef] [PubMed]
12. Pattin, C.A.; Caler, W.E.; Carter, D.R. Cyclic mechanical property degradation during fatigue loading of cortical bone. J. Biomech. 1996 , 29 , 69-79. [CrossRef] [PubMed]
13. Schaffler, M.; Radin, E.; Burr, D. Long-term fatigue behavior of compact bone at low strain magnitude and rate. Bone 1990 , 11 , 321-326. [CrossRef] [PubMed]
14. Carter, D.R.; Caler, W.E.; Spengler, D.M.; Frankel, V.H. Fatigue Behavior of Adult Cortical Bone: The Influence of Mean Strain and Strain Range. Acta Orthop. 1981 , 52 , 481-490. [CrossRef]
15. Burr, D.B.; Turner, C.H.; Naick, P.; Forwood, M.R.; Ambrosius, W.; Hasan, M.S.; Pidaparti, R. Does microdamage accumulation affect the mechanical properties of bone? J. Biomech. 1998 , 31 , 337-345. [CrossRef] [PubMed]
16. Chamay, A.; Tschantz, P. Mechanical influences in bone remodeling. Experimental research on Wolff's law. J. Biomech. 1972 , 5 , 173-180. [CrossRef] [PubMed]
17. Burr, D.B.; Martin, R.; Schaffler, M.B.; Radin, E.L. Bone remodeling in response to in vivo fatigue microdamage. J. Biomech. 1985 , 18 , 189-200. [CrossRef] [PubMed]
18. Gross, T.S.; Edwards, J.L.; Mcleod, K.J.; Rubin, C.T. Strain gradients correlate with sites of periosteal bone formation. J. Bone Miner. Res. 1997 , 12 , 982-988. [CrossRef]
19. Sinclair, J.; Fau-Goodwin, J.; Richards, J.; Shore, H. The influence of minimalist and maximalist footwear on the kinetics and kinematics of running. Footwear Sci. 2016 , 8 , 33-39. [CrossRef]
20. Esculier, J.-F.; Dubois, B.; Dionne, C.E.; Leblond, J.; Roy, J.-S. A consensus definition and rating scale for minimalist shoes. J. Foot Ankle Res. 2015 , 8 , 42. [CrossRef] [PubMed]
21. Zandbergen, M.A.; Ter Wengel, X.J.; van Middelaar, R.P.; Buurke, J.H.; Veltink, P.H.; Reenalda, J. Peak tibial acceleration should not be used as indicator of tibial bone loading during running. Sports Biomech. 2023 , 1-18. [CrossRef] [PubMed]
22. Sinclair, J.; Hobbs, S.; Currigan, G.; Taylor, P. A comparison of several barefoot inspired footwear models in relation to barefoot and conventional running footwear. Comp. Exerc. Physiol. 2013 , 9 , 13-21. [CrossRef]
23. Hannigan, J.; Pollard, C.D. Differences in running biomechanics between a maximal, traditional, and minimal running shoe. J. Sci. Med. Sport 2020 , 23 , 15-19. [CrossRef] [PubMed]
24. Chan, Z.Y.S.; Au, I.P.H.; Lau, F.O.Y.; Ching, E.C.K.; Zhang, J.H.; Cheung, R.T.H. Does maximalist footwear lower impact loading during level ground and downhill running? Eur. J. Sport Sci. 2018 , 18 , 1083-1089. [CrossRef]
25. Edwards, W.B.; Taylor, D.; Rudolphi, T.J.; Gillette, J.C.; Derrick, T.R. Effects of Stride Length and Running Mileage on a Probabilistic Stress Fracture Model. Med. Sci. Sports Exerc. 2009 , 41 , 2177-2184. [CrossRef]
26. Edwards, W.B.; Taylor, D.; Rudolphi, T.J.; Gillette, J.C.; Derrick, T.R. Effects of running speed on a probabilistic stress fracture model. Clin. Biomech. 2010 , 25 , 372-377. [CrossRef]
27. Sinclair, J.; Brooks, D.; Taylor, P.J.; Liles, N.B. Effects of running in minimal, maximal and traditional running shoes: A musculoskeletal simulation exploration using statistical parametric mapping and Bayesian analyses. Footwear Sci. 2021 , 13 , 143-156. [CrossRef]

28. Cappozzo, A.; Catani, F.; Della Croce, U.; Leardini, A. Position and orientation in space of bones during movement: Anatomical frame definition and determination. Clin. Biomech. 1995 , 10 , 171-178. [CrossRef]
29. Sinclair, J.; Taylor, P .J.; Hobbs, S.J. Digital Filtering of Three-Dimensional Lower Extremity Kinematics: An Assessment. J. Hum. Kinet. 2013 , 39 , 25-36. [CrossRef]
30. Addison, B.J.; Lieberman, D.E. Tradeoffs between impact loading rate, vertical impulse and effective mass for walkers and heel strike runners wearing footwear of varying stiffness. J. Biomech. 2015 , 48 , 1318-1324. [CrossRef]
31. Lieberman, D.E.; Venkadesan, M.; Werbel, W.A.; Daoud, A.I.; D'andrea, S.; Davis, I.S.; Mang'eni, R.O.; Pitsiladis, Y. Foot strike patterns and collision forces in habitually barefoot versus shod runners. Nature 2010 , 463 , 531-535. [CrossRef] [PubMed]
32. Chi, K.-J.; Schmitt, D. Mechanical energy and effective foot mass during impact loading of walking and running. J. Biomech. 2005 , 38 , 1387-1395. [CrossRef] [PubMed]
33. Squadrone, R.; Rodano, R.; Hamill, J.; Preatoni, E. Acute effect of different minimalist shoes on foot strike pattern and kinematics in rearfoot strikers during running. J. Sports Sci. 2014 , 33 , 1196-1204. [CrossRef] [PubMed]
34. Sinclair, J.; Huang, G.; Taylor, P.J.; Chockalingam, N.; Fan, Y. Effects of Running in Minimal and Conventional Footwear on Medial Tibiofemoral Cartilage Failure Probability in Habitual and Non-Habitual Users. J. Clin. Med. 2022 , 11 , 7335. [CrossRef] [PubMed]
35. Lerner, Z.F.; DeMers, M.S.; Delp, S.L.; Browning, R.C. How tibiofemoral alignment and contact locations affect predictions of medial and lateral tibiofemoral contact forces. J. Biomech. 2015 , 48 , 644-650. [CrossRef]
36. Delp, S.L.; Anderson, F.C.; Arnold, A.S.; Loan, P.; Habib, A.; John, C.T.; Guendelman, E.; Thelen, D.G. OpenSim: Open-Source Software to Create and Analyze Dynamic Simulations of Movement. IEEE Trans. Biomed. Eng. 2007 , 54 , 1940-1950. [CrossRef]
37. Steele, K.M.; DeMers, M.S.; Schwartz, M.H.; Delp, S.L. Compressive tibiofemoral force during crouch gait. Gait Posture 2012 , 35 , 556-560. [CrossRef]
38. Herzog, W.; Clark, A.; Wu, J. Resultant and local loading in models of joint disease. Arthritis Care Res. Off. J. Am. Coll. Rheumatol. 2003 , 49 , 239-247. [CrossRef]
39. van Arkel, R.J.; Modenese, L.; Phillips, A.T.; Jeffers, J.R. Hip abduction can prevent posterior edge loading of hip replacements. J. Orthop. Res. 2013 , 31 , 1172-1179. [CrossRef]
40. Keast, M.; Bonacci, J.; Fox, A. Geometric variation of the human tibia-fibula: A public dataset of tibia-fibula surface meshes and statistical shape model. PeerJ 2023 , 11 , e14708. [CrossRef]
41. Chen, T.; An, W.; Chan, Z.; Au, I.; Zhang, Z.; Cheung, R. Immediate effects of modified landing pattern on a probabilistic tibial stress fracture model in runners. Clin. Biomech. 2016 , 33 , 49-54. [CrossRef] [PubMed]
42. Bruce, O.L.; Baggaley, M.; Khassetarash, A.; Haider, I.T.; Edwards, W.B. Tibial-fibular geometry and density variations associated with elevated bone strain and sex disparities in young active adults. Bone 2022 , 161 , 116443. [CrossRef]
43. Haider, I.T.; Baggaley, M.; Edwards, W.B. Subject-Specific Finite Element Models of the Tibia with Realistic Boundary Conditions Predict Bending Deformations Consistent with In Vivo Measurement. J. Biomech. Eng. 2020 , 142 , 021010. [CrossRef] [PubMed]
44. Baggaley, M.; Haider, I.; Bruce, O.; Khassetarash, A.; Edwards, W.B. Tibial Strains During Graded Running. arXiv 2023 , arXiv:2305.04139.
45. Sinclair, J.; Chockalingam, N.; Taylor, P.J. Lower Extremity Kinetics and Kinematics in Runners with Patellofemoral Pain: A Retrospective Case-Control Study Using Musculoskeletal Simulation. Appl. Sci. 2022 , 12 , 585. [CrossRef]
46. Carter, D.R.; Caler, W.E. A cumulative damage model for bone fracture. J. Orthop. Res. 1985 , 3 , 84-90. [CrossRef]
47. Turner, C.H.; Forwood, M.; Rho, J.; Yoshikawa, T. Mechanical loading thresholds for lamellar and woven bone formation. J. Bone Miner. Res. 1994 , 9 , 87-97. [CrossRef]
48. Taylor, D.; Casolari, E.; Bignardi, C. Predicting stress fractures using a probabilistic model of damage, repair and adaptation. J. Orthop. Res. 2004 , 22 , 487-494. [CrossRef]
49. Weibull, W. A Statistical Distribution Function of Wide Applicability. J. Appl. Mech. 1951 , 18 , 293-297. [CrossRef]
50. Taylor, D.; Kuiper, J.H. The prediction of stress fractures using a 'stressed volume' concept. J. Orthop. Res. 2001 , 19 , 919-926. [CrossRef]
51. Cohen, J. Statistical Power Analysis for the Behavioral Sciences , 2nd ed.; Lawrence Erlbaum Associates: Hillsdale, NJ, USA, 1988.
52. Kardouni, J.R.; McKinnon, C.J.; Taylor, K.M.; Hughes, J.M. Timing of Stress Fractures in Soldiers During the First 6 Career Months: ARetrospective Cohort Study. J. Athl. Train. 2021 , 56 , 1278-1284. [CrossRef] [PubMed]
53. Bruce, O.L.; Edwards, W.B. Sex disparities in tibia-fibula geometry and density are associated with elevated bone strain in females: Across-validation study. Bone 2023 , 173 , 116803. [CrossRef] [PubMed]

Disclaimer/Publisher's Note: The statements, opinions and data contained in all publications are solely those of the individual author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to people or property resulting from any ideas, methods, instructions or products referred to in the content.