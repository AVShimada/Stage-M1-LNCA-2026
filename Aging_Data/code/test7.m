%% ========================================================================
%  REPRODUCTION FINALE DE LA FIGURE 4D (N=49 SUJETS, TR=2.0)
%% ========================================================================

% 1. PARAMÈTRES
N = 49; 
TR = 2.0; 
win_ranges = { [60 210], [15 60] }; % Secondes
range_names = {'Long Windows (60-210s)', 'Mid Windows (15-60s)'};

% Stockage : [Sujets x Conditions (Emp, PR, SH)]
Vtyp_results = cell(2,1); 
for r = 1:2, Vtyp_results{r} = zeros(N, 3); end

fprintf('Calcul des Vtyp pour le groupe (%d sujets)...\n', N);

% 2. BOUCLE DE TRAITEMENT
for s = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', s));
    TS_emp = SUBJECT.TS;
    
    % --- Génération des Surrogates ---
    % Phase-randomized (Null hypothesis: stationarity) [cite: 521, 527]
    TS_pr = PhaseRand_surrogates(TS_emp); 
    
    for r = 1:2
        w_range = round(win_ranges{r} / TR);
        tmp_e = []; tmp_p = []; tmp_s = [];
        
        % On parcourt la gamme de fenêtres [cite: 523]
        for w = w_range(1):10:w_range(2)
            % Flux dFC
            s_emp = TS2dFCstream(TS_emp, w, 1);
            s_pr  = TS2dFCstream(TS_pr, w, 1);
            % Shuffled (Null hypothesis: no seq. correlations) [cite: 522, 535]
            s_sh  = s_emp(:, randperm(size(s_emp, 2))); 
            
            % Vitesses instantanées [cite: 274]
            [~, v_e] = dFC_Speeds(s_emp, w);
            [~, v_p] = dFC_Speeds(s_pr, w);
            [~, v_s] = dFC_Speeds(s_sh, w);
            
            tmp_e = [tmp_e; v_e]; tmp_p = [tmp_p; v_p]; tmp_s = [tmp_s; v_s];
        end
        
        % Extraction du Vtyp (Vitesse typique par sujet) [cite: 20, 73]
        Vtyp_results{r}(s, 1) = median(tmp_e);
        Vtyp_results{r}(s, 2) = median(tmp_p);
        Vtyp_results{r}(s, 3) = median(tmp_s);
    end
    if mod(s,10)==0, fprintf('Sujet %d/49 terminé\n', s); end
end

%% ========================================================================
% 3. VISUALISATION ET TESTS STATISTIQUES (KS-TEST)
%% ========================================================================
figure('Name', 'Figure 4D - dFC Speed Distributions', 'Color', 'k');

for r = 1:2
    subplot(2, 1, r); hold on;
    data = Vtyp_results{r};
    
    % KDE [cite: 523]
    [f1, x1] = ksdensity(data(:,1)); % Empirique (Bleu)
    [f2, x2] = ksdensity(data(:,2)); % Phase Rand (Vert)
    [f3, x3] = ksdensity(data(:,3)); % Shuffled (Rouge)
    
    % Tracé des courbes [cite: 523]
    p1 = plot(x1, f1, 'Color', [0.1 0.1 0.5], 'LineWidth', 3, 'DisplayName', 'Empirical');
    p2 = plot(x2, f2, 'g--', 'LineWidth', 2, 'DisplayName', 'Phase rand');
    p3 = plot(x3, f3, 'r:', 'LineWidth', 2, 'DisplayName', 'Shuffled');
    
    % Tests de Kolmogorov-Smirnov 
    [~, p_pr] = kstest2(data(:,1), data(:,2));
    [~, p_sh] = kstest2(data(:,1), data(:,3));
    
    % Ajout des étoiles de significativité 
    y_max = max([f1, f2, f3]);
    if p_pr < 0.01, text(x1(f1==max(f1))-0.05, max(f1)+0.1, '**', 'Color', 'g', 'FontSize', 15); end
    if p_sh < 0.01, text(x1(f1==max(f1))+0.05, max(f1)+0.1, '**', 'Color', 'r', 'FontSize', 15); end

    title(range_names{r}); xlabel('V_{typ}'); ylabel('Prob. density');
    legend([p1 p2 p3], 'Location', 'northeast', 'Box', 'off');
    grid on; xlim([0 1.2]);
end