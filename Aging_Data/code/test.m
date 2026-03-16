%% ==========================================
% Dynamic Functional Connectivity Pipeline
% (with Meta-Connectivity)
% ==========================================

%% PARAMETERS

N = 49;
TR = 2;

window = round(20/TR);
step   = 1;

%% STORAGE

ages       = zeros(N,1);
speed_all  = zeros(N,1);
corr_all   = zeros(N,1);

%% ==========================================
% MAIN LOOP
%% ==========================================

for s = 1:N

    SUBJECT = eval(sprintf('SUBJECT_%d',s));

    TS = SUBJECT.TS;
    ages(s) = SUBJECT.age;

    %% 1️⃣ dFC stream

    dFCstream = TS2dFCstream(TS,window,step);

    SUBJECT.dFCstream = dFCstream;

    %% 2️⃣ dFC matrix

    dFC = dFCstream2dFC(dFCstream);

    SUBJECT.dFC = dFC;

    %% 3️⃣ META-CONNECTIVITY

    MC = dFCstream2MC(dFCstream);

    SUBJECT.MC = MC;

    %% 4️⃣ dFC SPEED

    [typSpeed,Speeds] = dFC_Speeds(dFCstream);

    SUBJECT.dFC_speed  = typSpeed;
    SUBJECT.dFC_speeds = Speeds;

    speed_all(s) = typSpeed;

    %% 5️⃣ FC similarity (20 s)

    lag = round(20/TR);

    corr_all(s) = mean(diag(dFC,lag));

    SUBJECT.FC_similarity_20s = corr_all(s);

    eval(sprintf('SUBJECT_%d = SUBJECT;',s));

end

%% ==========================================
% VISUALIZATION
%% ==========================================

SUBJECT = SUBJECT_1;

figure
imagesc(SUBJECT.dFC)
axis square
colorbar
colormap(turbo)

title('Dynamic Functional Connectivity')

figure
imagesc(SUBJECT.MC)
axis square
colorbar
colormap(turbo)

title('Meta-Connectivity Matrix')

%% AGE vs dFC SPEED

mdl_speed = fitlm(ages,speed_all);

figure
scatter(ages,speed_all,70,'filled')
hold on
plot(ages,mdl_speed.Fitted,'r','LineWidth',2)

xlabel('Age')
ylabel('dFC Speed')

title('Dynamic FC Speed vs Age')
=======
%% ==========================================
% Dynamic Functional Connectivity Pipeline
% (with Meta-Connectivity)
% ==========================================

%% PARAMETERS

N = 49;
TR = 2;

window = round(20/TR);
step   = 1;

%% STORAGE

ages       = zeros(N,1);
speed_all  = zeros(N,1);
corr_all   = zeros(N,1);

%% ==========================================
% MAIN LOOP
%% ==========================================

for s = 1:N

    SUBJECT = eval(sprintf('SUBJECT_%d',s));

    TS = SUBJECT.TS;
    ages(s) = SUBJECT.age;

    %% 1️⃣ dFC stream

    dFCstream = TS2dFCstream(TS,window,step);

    SUBJECT.dFCstream = dFCstream;

    %% 2️⃣ dFC matrix

    dFC = dFCstream2dFC(dFCstream);

    SUBJECT.dFC = dFC;

    %% 3️⃣ META-CONNECTIVITY

    MC = dFCstream2MC(dFCstream);

    SUBJECT.MC = MC;

    %% 4️⃣ dFC SPEED

    [typSpeed,Speeds] = dFC_Speeds(dFCstream);

    SUBJECT.dFC_speed  = typSpeed;
    SUBJECT.dFC_speeds = Speeds;

    speed_all(s) = typSpeed;

    %% 5️⃣ FC similarity (20 s)

    lag = round(20/TR);

    corr_all(s) = mean(diag(dFC,lag));

    SUBJECT.FC_similarity_20s = corr_all(s);

    eval(sprintf('SUBJECT_%d = SUBJECT;',s));

end

%% ==========================================
% VISUALIZATION
%% ==========================================

SUBJECT = SUBJECT_1;

figure
imagesc(SUBJECT.dFC)
axis square
colorbar
colormap(turbo)

title('Dynamic Functional Connectivity')

figure
imagesc(SUBJECT.MC)
axis square
colorbar
colormap(turbo)

title('Meta-Connectivity Matrix')

%% AGE vs dFC SPEED

mdl_speed = fitlm(ages,speed_all);

figure
scatter(ages,speed_all,70,'filled')
hold on
plot(ages,mdl_speed.Fitted,'r','LineWidth',2)

xlabel('Age')
ylabel('dFC Speed')

title('Dynamic FC Speed vs Age')
grid on